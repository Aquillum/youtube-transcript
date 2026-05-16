from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
import os
import re

app = Flask(__name__)
INTERNAL_DIR = Path(os.getenv('TRANSCRIPT_OUTPUT_DIR', '/internal'))

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
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
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=os.getenv('FLASK_DEBUG', '0') == '1') 