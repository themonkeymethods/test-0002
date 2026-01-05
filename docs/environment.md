# Environment configuration

This document describes the environment variables, path resolution behavior, and generated files for the Building Magazine app.

## Backend environment variables

The backend reads configuration from environment variables (typically loaded from `backend/.env`). The installer (`install.sh`) creates this file if it does not exist.

| Variable | Required | Default (install.sh) | Purpose |
| --- | --- | --- | --- |
| `APP_ENV` | No | `local` | Environment name for operators (informational; useful for logging or tooling). |
| `DATABASE_URL` | Yes | `sqlite:////absolute/path/to/backend/app.db` | Database connection string. For SQLite, use `sqlite:////absolute/path` (four slashes) for an absolute path. |
| `UVICORN_HOST` | No | `0.0.0.0` | Bind address for the FastAPI server. |
| `UVICORN_PORT` | No | `8000` | Port for the FastAPI server. |
| `SUPERUSER_EMAIL` | No | `admin@example.com` | Seeded superuser email used by `install.sh` when initializing the database. |
| `SUPERUSER_PASSWORD` | No | `changeme` | Seeded superuser password used by `install.sh` when initializing the database. |

> **Note:** The FastAPI app currently does not read these variables directly. They are consumed by tooling (`install.sh`, systemd unit) and by the `uvicorn` launch command in the systemd unit.

## Frontend environment variables

The frontend does not currently read any environment variables. If you add API configuration later, Vite exposes variables prefixed with `VITE_` at build time. A common pattern is to add:

- `VITE_API_BASE_URL` — Base URL for the backend API (for example, `http://127.0.0.1:8000`).

## Path resolution expectations

- `DATABASE_URL` should be absolute for SQLite deployments (`sqlite:////abs/path/to/app.db`). The installer uses an absolute path so the database resolves consistently even when run via systemd.
- The systemd unit sets `WorkingDirectory` to `backend/`, so any relative paths in the backend process resolve from that directory.
- The frontend is built and served from the `frontend/` directory; relative paths in the Vite config resolve from `frontend/`.

## Generated files

### Created by the installer

- `backend/.env`: Generated if missing. Stores the backend environment variables listed above.
- `backend/app.db`: SQLite database created by `install.sh` using `backend/db/schema.sql`.
- systemd unit:
  - `/etc/systemd/system/building-magazine-backend.service` (when run as root), or
  - `~/.config/systemd/user/building-magazine-backend.service` (non-root user).

### Recommended system-wide env files (for ops deployments)

If you want to standardize configuration outside the repo, you can generate system-wide env files and point your service manager at them. A common convention is:

- `/etc/building-magazine/paths.env` — path and runtime metadata.
- `/etc/building-magazine/building-magazine.env` — application configuration (the same keys as `backend/.env`).

These files are not created by the repository scripts today, but are listed here as suggested locations for production or managed deployments.

## Example env files

- Backend: [`backend/.env.example`](../backend/.env.example)
- Frontend: [`frontend/.env.example`](../frontend/.env.example)
