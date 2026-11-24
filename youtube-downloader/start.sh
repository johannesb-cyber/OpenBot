#!/usr/bin/env bash
# Startet den YouTube Downloader (macOS / Linux)
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q --upgrade -r requirements.txt
python app.py
