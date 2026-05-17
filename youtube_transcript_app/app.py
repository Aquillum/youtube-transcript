from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
from yt_dlp import YoutubeDL
from typing import Any
from xml.etree import ElementTree
from urllib import request as urlrequest
from urllib import error as urlerror
import html
import json
import os
import re
import time

app = Flask(__name__)
INTERNAL_DIR = Path(os.getenv('TRANSCRIPT_OUTPUT_DIR', '/internal'))
COOKIES_FILE = os.getenv('YOUTUBE_COOKIES_FILE', '').strip()


def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def transcript_list_to_text(transcript_list):
    return ' '.join(entry.get('text', '') for entry in transcript_list).strip()


def fetch_transcript_via_api(video_id: str) -> str:
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            return transcript_list_to_text(YouTubeTranscriptApi.get_transcript(video_id))
        except Exception as exc:
            last_exc = exc
            if attempt == 0 and 'no element found' in str(exc).lower():
                app.logger.warning('Empty transcript response for %s; retrying once', video_id)
                time.sleep(1)
                continue
            raise

    if last_exc is not None:
        raise last_exc
    raise RuntimeError('Failed to fetch transcript')


def _select_caption_language(captions, preferred_langs=None):
    if not captions:
        return None

    keys = list(captions.keys())
    preferred_langs = preferred_langs or []

    for preferred in preferred_langs:
        if not preferred:
            continue
        preferred_lower = preferred.lower()
        for key in keys:
            key_lower = key.lower()
            if key_lower == preferred_lower or key_lower.startswith(preferred_lower):
                return key

    return keys[0]


def _caption_payload_to_text(payload, ext):
    payload = payload.strip()
    if not payload:
        return ''

    ext = (ext or '').lower()

    if ext == 'json3' or payload.startswith('{'):
        data = json.loads(payload)
        parts = []
        for event in data.get('events', []):
            segs = event.get('segs') or []
            text = ''.join(seg.get('utf8', '') for seg in segs).strip()
            if text:
                parts.append(text)
        return ' '.join(parts).strip()

    if ext in {'srv3', 'xml'} or payload.startswith('<'):
        root = ElementTree.fromstring(payload)
        parts = []
        for node in root.iter():
            if node.tag.lower().endswith('text') and node.text:
                parts.append(node.text.strip())
        return ' '.join(parts).strip()

    lines = []
    for line in payload.splitlines():
        line = line.strip()
        if not line or line == 'WEBVTT' or '-->' in line or line.isdigit():
            continue
        line = re.sub(r'<[^>]+>', '', line)
        line = html.unescape(line).strip()
        if line:
            lines.append(line)
    return ' '.join(lines).strip()


def fetch_transcript_via_ytdlp(video_url) -> str:
    ydl_opts: dict[str, Any] = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'skip_download': True,
        'retries': 2,
        'extractor_retries': 2,
    }

    if COOKIES_FILE and Path(COOKIES_FILE).exists():
        ydl_opts['cookiefile'] = COOKIES_FILE

    with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
        info = ydl.extract_info(video_url, download=False)

    captions = info.get('subtitles') or {}
    if not captions:
        captions = info.get('automatic_captions') or {}

    lang = _select_caption_language(
        captions,
        preferred_langs=[info.get('language'), 'en', 'en-US', 'en-GB']
    )
    if not lang:
        raise RuntimeError('No subtitles or automatic captions were exposed by YouTube')

    formats = captions.get(lang) or []
    if not formats:
        raise RuntimeError(f'No caption formats available for language {lang}')

    # Prefer the first caption URL we get.
    preferred = next((fmt for fmt in formats if fmt.get('url')), None)
    if not preferred:
        raise RuntimeError(f'No downloadable caption URL available for language {lang}')

    try:
        with urlrequest.urlopen(preferred['url'], timeout=30) as response:
            payload = response.read().decode('utf-8', 'ignore')
    except urlerror.URLError as exc:
        raise RuntimeError(f'Could not download caption payload: {exc}') from exc

    text = _caption_payload_to_text(payload, preferred.get('ext'))
    if not text:
        raise RuntimeError('Caption payload was empty')

    return text


def fetch_transcript_text(video_url: str, video_id: str) -> str:
    try:
        return fetch_transcript_via_api(video_id)
    except Exception as api_exc:
        app.logger.warning('youtube_transcript_api failed for %s: %s', video_id, api_exc)

    return fetch_transcript_via_ytdlp(video_url)


def transcript_error_message(exc):
    name = exc.__class__.__name__
    message = str(exc).strip()
    lower = message.lower()

    if 'sign in to confirm you' in lower and 'bot' in lower:
        if COOKIES_FILE:
            return 'YouTube is still blocking automated access even with the current cookies file.'
        return 'YouTube is blocking automated access from this server. Add a cookies file from a logged-in browser and set YOUTUBE_COOKIES_FILE.'
    if 'cookie' in lower and 'youtube' in lower:
        return 'YouTube needs cookies for this request. Mount a cookies file and set YOUTUBE_COOKIES_FILE.'
    if 'no element found' in lower:
        return 'YouTube returned an empty transcript response. This usually means YouTube is blocking the request or the transcript endpoint changed.'
    if name == 'NoTranscriptAvailable':
        return 'No transcript is available for this video.'
    if name == 'NoTranscriptFound':
        return 'No transcript was found in the selected language.'
    if name == 'TranscriptsDisabled':
        return 'This video has subtitles disabled, so no transcript is available.'
    if name == 'TooManyRequests':
        return 'YouTube rate-limited the request. Please try again later.'
    if name == 'VideoUnavailable':
        return 'This video is unavailable.'
    if message:
        return message
    return 'Could not retrieve a transcript for this video.'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    video_id = None
    try:
        data = request.get_json() or {}
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400

        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        transcript_text = fetch_transcript_text(video_url, video_id)

        # Save a copy inside the mounted volume so the host gets the text file too.
        INTERNAL_DIR.mkdir(parents=True, exist_ok=True)
        output_file = INTERNAL_DIR / f"youtube-transcript-{video_id}.txt"
        output_file.write_text(transcript_text, encoding='utf-8')

        return jsonify({
            'success': True,
            'transcript': transcript_text,
            'saved_to': str(output_file)
        })

    except Exception as exc:
        app.logger.exception('Transcript error for video_id=%s', video_id)
        lower = str(exc).lower()
        status = 403 if 'sign in to confirm' in lower and 'bot' in lower else 404 if any(k in exc.__class__.__name__ for k in ['NoTranscript', 'TranscriptsDisabled', 'VideoUnavailable']) else 500
        return jsonify({'error': transcript_error_message(exc)}), status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG', '0') == '1')
