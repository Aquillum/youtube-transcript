# Docker Quick Start

## Build

From the folder with `docker-compose.yaml`:

```bash
docker compose build
```

Optional clean rebuild:

```bash
docker compose build --no-cache
```

## Start

```bash
docker compose up -d
```

## Logs

```bash
docker compose logs -f
```

## Stop

```bash
docker compose down
```

## Open the app

```text
http://localhost:5000
```

## Important paths

- App inside container: `/internal`
- Host transcript folder: `./data/transcoded`
- Optional cookies file: mount it into the container and set `YOUTUBE_COOKIES_FILE`

## Project structure

```text
.
├── Dockerfile
├── docker-compose.yaml
├── README-DOCKER-SHORT.md
├── data/
│   └── transcoded/
└── youtube_transcript_app/
    ├── app.py
    ├── requirements.txt
    ├── templates/
    │   └── index.html
    └── static/
        ├── css/
        │   └── style.css
        └── js/
            └── script.js
```

## Raspberry Pi 4 note

- Works as long as Docker and Docker Compose are installed.
- Run all commands from the project folder so the relative volume path works.
