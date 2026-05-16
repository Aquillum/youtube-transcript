# YouTube Transcript Extractor Project

## Overview
This project provides a modern web application for extracting and downloading transcripts from YouTube videos. Built with Python (Flask) backend and a clean, responsive frontend, it offers an easy way to access video transcripts without any API keys or costs.

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main.png)
*Clean and simple interface for entering YouTube URLs*

### Loading State
![Loading State](screenshots/loading.png)
*Smooth loading animation while fetching transcript*

### Transcript Display
![Transcript Display](screenshots/transcript.png)
*Transcript display with download option*

## 🌟 Key Features
- **Easy Transcript Extraction**: Simply paste a YouTube URL and get the transcript
- **Modern UI/UX**: Clean, responsive design with loading states and error handling
- **Free to Use**: No API keys or authentication required
- **Download Support**: Save transcripts as text files
- **Real-time Validation**: Instant feedback on URL validity

## 🛠️ Tech Stack
- **Backend**: Python 3.7+ with Flask
- **Frontend**: HTML5, CSS3, Modern JavaScript
- **APIs**: youtube_transcript_api
- **Design**: Responsive CSS with modern aesthetics

## 📁 Project Structure
```
youtube_transcript_app/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Application styling
│   └── js/
│       └── script.js     # Frontend functionality
├── templates/
│   └── index.html        # Main application template
└── README.md             # Application-specific documentation
```

## 🚀 Quick Start
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the application directory:
   ```bash
   cd youtube_transcript_app
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip3 install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   python3 app.py
   ```

5. Open `http://localhost:5000` in your browser

## 🐳 Docker
A Docker setup is included at the repo root (`Dockerfile` and `docker-compose.yaml`).
For the full Docker instructions, see `README-DOCKER.md`; for a shorter version, see `README-DOCKER-SHORT.md`.

## 💡 Use Cases
- Content creators needing video transcripts
- Students accessing lecture transcripts
- Researchers collecting video content
- Accessibility enhancement for video content
- Content analysis and text extraction

## ⚠️ Important Notes
- Works only with public YouTube videos having available captions
- Respects YouTube's terms of service and public API limitations
- See detailed limitations in `youtube_transcript_app/README.md`

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🔍 Future Enhancements
- [ ] Support for multiple language selection
- [ ] Batch processing of multiple videos
- [ ] Advanced formatting options for downloaded transcripts
- [ ] Integration with other video platforms
- [ ] API endpoint for programmatic access

## 🐛 Known Issues
See the detailed limitations and known issues section in `youtube_transcript_app/README.md`

## 📫 Contact
For any queries or support, please open an issue in the repository.

## 🙏 Acknowledgments
- YouTube Transcript API developers
- Flask framework community
- All contributors and users of this project 