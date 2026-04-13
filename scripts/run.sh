#!/bin/sh
set -e

uv run gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2
