#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ]; then
  echo 'Create the virtual environment and install dependencies first; see README.md.'
  exit 1
fi
if [ ! -f frontend/dist/index.html ]; then
  echo 'Build the frontend first: pnpm --dir frontend build'
  exit 1
fi
cd backend
exec ../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
