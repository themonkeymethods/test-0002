#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
ENV_FILE="$BACKEND_DIR/.env"
DB_PATH="$BACKEND_DIR/app.db"
SCHEMA_FILE="$BACKEND_DIR/db/schema.sql"
SERVICE_NAME="building-magazine-backend.service"

log() {
  printf "\n[%s] %s\n" "$(date +%H:%M:%S)" "$*"
}

require_tool() {
  local tool="$1"
  if ! which "$tool" >/dev/null 2>&1; then
    echo "Missing required tool: $tool" >&2
    exit 1
  fi
  local path
  path="$(which "$tool")"
  echo "$tool -> $path"
}

detect_os() {
  local os
  os="$(uname -s)"
  case "$os" in
    Linux|Darwin)
      echo "$os"
      ;;
    *)
      echo "Unsupported OS: $os" >&2
      exit 1
      ;;
  esac
}

ensure_env_file() {
  if [[ -f "$ENV_FILE" ]]; then
    log "Env file already exists at $ENV_FILE"
    return
  fi

  log "Creating env file at $ENV_FILE"
  cat <<EOF_ENV > "$ENV_FILE"
APP_ENV=local
DATABASE_URL=sqlite:///$DB_PATH
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=changeme
EOF_ENV
}

setup_backend() {
  log "Setting up backend virtualenv and dependencies"
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
}

setup_frontend() {
  log "Installing frontend dependencies"
  (cd "$FRONTEND_DIR" && npm install)
}

init_db() {
  log "Initializing database"
  mkdir -p "$(dirname "$DB_PATH")"
  if [[ ! -f "$SCHEMA_FILE" ]]; then
    echo "Missing schema file at $SCHEMA_FILE" >&2
    exit 1
  fi

  sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

  local email password
  email="${SUPERUSER_EMAIL:-admin@example.com}"
  password="${SUPERUSER_PASSWORD:-changeme}"

  sqlite3 "$DB_PATH" <<SQL
INSERT OR IGNORE INTO accounts (email, password, is_superuser)
VALUES ('$email', '$password', 1);
SQL
}

install_systemd_service() {
  if ! which systemctl >/dev/null 2>&1; then
    log "systemctl not available; skipping systemd unit install"
    return
  fi

  local target_dir unit_path
  if [[ $EUID -eq 0 ]]; then
    target_dir="/etc/systemd/system"
  else
    target_dir="$HOME/.config/systemd/user"
    mkdir -p "$target_dir"
  fi

  unit_path="$target_dir/$SERVICE_NAME"

  log "Installing systemd unit at $unit_path"
  cat <<EOF_UNIT > "$unit_path"
[Unit]
Description=Building Magazine Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=$BACKEND_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host \${UVICORN_HOST} --port \${UVICORN_PORT}
Restart=on-failure

[Install]
WantedBy=default.target
EOF_UNIT

  if [[ $EUID -eq 0 ]]; then
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl restart "$SERVICE_NAME" || true
  else
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME"
    systemctl --user restart "$SERVICE_NAME" || true
  fi
}

health_check() {
  log "Running health check"
  if ! which curl >/dev/null 2>&1; then
    log "curl not available; skipping health check"
    return
  fi

  local url
  url="http://127.0.0.1:${UVICORN_PORT:-8000}/"
  curl --fail --silent "$url" >/dev/null && log "Health check passed: $url" || {
    echo "Health check failed. Ensure the service is running at $url" >&2
    return 1
  }
}

main() {
  log "Detecting OS"
  detect_os

  log "Validating required tools"
  require_tool python3
  require_tool pip
  require_tool node
  require_tool npm
  require_tool sqlite3

  log "Ensuring env file"
  ensure_env_file

  setup_backend
  setup_frontend
  init_db
  install_systemd_service
  health_check

  log "Install completed"
}

main "$@"
