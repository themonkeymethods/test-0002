# Installation Guide

This repository includes a one-stop installer that validates tooling, sets up the backend and frontend, prepares a local database, and installs a systemd unit.

## Usage

```bash
./install.sh
```

## What the script does

- Validates required tools (`python3`, `pip`, `node`, `npm`, `sqlite3`, `curl`).
- Creates `backend/.venv` and installs backend dependencies from `backend/requirements.txt`.
- Installs frontend dependencies from `frontend/package.json`.
- Generates `backend/.env` with default settings if it does not exist.
- Initializes `backend/app.db` and applies schema migrations from `backend/db/schema.sql`.
- Seeds a superuser account using values from `backend/.env`.
- Installs a systemd unit for the backend and attempts to start it.
- Runs a health check against `http://127.0.0.1:8000/`.

## Configuration

Update `backend/.env` to customize settings:

```env
APP_ENV=local
DATABASE_URL=sqlite:///backend/app.db
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=changeme
```

## Notes

- If you run the script as a non-root user, the systemd unit is installed under `~/.config/systemd/user/`.
- If systemd is unavailable (for example on macOS), the script skips unit installation.
