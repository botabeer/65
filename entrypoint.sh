#!/bin/bash

if [ "$ENV_MODE" = "dev" ]; then
    echo "Starting in Development Mode..."
    python app.py
else
    echo "Starting in Production Mode..."
    gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 30 --access-logfile - --error-logfile -
fi
