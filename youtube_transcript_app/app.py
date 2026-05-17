from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
from typing import Any
import os
import re
import time

app = Flask(__name__)
INTERNAL_DIR = Path(os.getenv('TRANSCRIPT_OUTPUT_DIR', '/internal'))


def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:v=|\\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\\.be\\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript_with_retry(video_id: str) -> list[dict[str, Any]]:
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            return YouTubeTranscriptApi.get_transcript(video_id)
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


def transcript_error_message(exc: Exception) -> str:
    name = exc.__class__.__name__
    message = str(exc).strip()

    if name == 'TranscriptsDisabled':
        return 'This video has subtitles disabled, so no transcript is available.'
    if name == 'NoTranscriptAvailable':
        return 'No transcript is available for this video.'
    if name == 'NoTranscriptFound':
        return 'No transcript was found in the selected language.'
    if name == 'TooManyRequests':
        return 'YouTube rate-limited the request. Please try again later.'
    if name == 'VideoUnavailable':
        return 'This video is unavailable.'
    if name == 'CouldNotRetrieveTranscript' and 'Request to YouTube failed' in message:
        return 'YouTube could not be reached for this video. Please try again later.'

    if 'no element found' in message.lower():
        return 'YouTube returned an empty transcript response. Please try again in a moment.'
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

        transcript_list = fetch_transcript_with_retry(video_id) or []

        # Format transcript
        formatted_transcript = ''
        for entry in transcript_list:
            formatted_transcript += f"{entry['text']} "

        transcript_text = formatted_transcript.strip()

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
        name = exc.__class__.__name__
        status = 429 if name == 'TooManyRequests' else 404 if name in {'TranscriptsDisabled', 'NoTranscriptAvailable', 'NoTranscriptFound', 'VideoUnavailable', 'CouldNotRetrieveTranscript'} else 500
        return jsonify({'error': transcript_error_message(exc)}), status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG', '0') == '1')
