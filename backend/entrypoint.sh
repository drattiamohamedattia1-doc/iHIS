#!/bin/sh
echo "Waiting for database..."
echo "Running database migrations..."
flask db upgrade
echo "Seeding initial data..."
python seed_data.py
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app