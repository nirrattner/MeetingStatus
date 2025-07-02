#!/bin/bash

NAME="MeetingStatus"
SOCKFILE=/home/nirrattner/Documents/MeetingStatus/run/gunicorn.sock
NUM_WORKERS=1
NUM_THREADS=4

cd /home/nirrattner/Documents/MeetingStatus

exec /home/nirrattner/Documents/MeetingStatus/.venv/bin/gunicorn run_server:app \
  --name $NAME \
  --workers $NUM_WORKERS \
  --threads $NUM_THREADS \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-