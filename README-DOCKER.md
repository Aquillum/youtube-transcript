# Docker Setup for YouTube Transcript Extractor

This file documents the local Docker build and start flow for the project, with Raspberry Pi 4 in mind.

## What this setup does

- Builds the Flask app into a Docker image
- Exposes the web app on port `5000`
- Stores exported transcript text files on the host in `./data/transcripts`
- Uses `gunicorn` inside the container instead of Flask's development server

## Project structure

```text
.
├── Dockerfile
├── docker-compose.yaml
├── README-DOCKER.md
├── data/
│   └── transcripts/
└── youtube_transcript_app/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── script.js
```

## Build information

### Docker image

The Dockerfile uses:

- `python:3.11-slim`
- `gunicorn`
- application code from `youtube_transcript_app/`

### Build command

Run this from the directory that contains `docker-compose.yaml`:

```bash
docker compose build
```

If you want to force a clean rebuild:

```bash
docker compose build --no-cache
```

## Start information

### Start the container

```bash
docker compose up -d
```

### View logs

```bash
docker compose logs -f
```

### Stop the container

```bash
docker compose down
```

## Local access

Open the app in a browser:

```text
http://localhost:5000
```

If you are using another machine on the network, replace `localhost` with the Raspberry Pi's IP address.

## Data storage

Transcript files are written inside the container to:

```text
/internal
```

and mounted to the host path:

```text
./data/transcripts
```

So the generated transcript text files will remain on the Raspberry Pi even after the container stops.

## Raspberry Pi 4 notes

- This setup should work on Raspberry Pi 4 as long as Docker and Docker Compose are installed.
- The base image is ARM-compatible, so no special cross-build setup should be needed.
- Make sure you run the commands in the folder where you copied the project, because the volume paths are relative to that folder.

## Recommended workflow

1. Copy the project into a folder on the Raspberry Pi.
2. Open a terminal in that folder.
3. Run `docker compose build`.
4. Run `docker compose up -d`.
5. Open `http://localhost:5000`.

## Troubleshooting

- If the transcript files are not showing up on the host, check that `./data/transcripts` exists and that the container has write permissions.
- If the app does not start, inspect logs with `docker compose logs -f`.
- If port `5000` is already in use, change the left side of the ports mapping in `docker-compose.yaml`.
- If you move the project into another folder, keep the `docker compose` commands tied to that folder so the relative volume path still resolves correctly.
