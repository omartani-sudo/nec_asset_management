#!/bin/bash
set -e

if [ "$1" = "migrate-only" ]; then
    echo "Running migrations only..."
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput --clear
    exit 0
fi

echo "Waiting for database..."

python -c "
import os
import time
import sys

database_url = os.environ.get('DATABASE_URL', '')
if not database_url:
    print('DATABASE_URL not set, skipping wait')
    sys.exit(0)

for i in range(30):
    try:
        import socket
        parts = database_url.split('@')
        if len(parts) > 1:
            host_port = parts[1].split('/')[0]
            host, port = host_port.split(':')
            port = int(port)
        else:
            host, port = 'db', 5432
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f'Database at {host}:{port} is ready!')
            sys.exit(0)
    except Exception:
        pass
    
    print(f'Database not ready yet... waiting ({i+1}/30)')
    time.sleep(2)

print('Database wait timed out, proceeding anyway...')
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ $# -eq 0 ]; then
    echo "Starting Gunicorn..."
    exec gunicorn nec_asset_management.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers 3 \
      --timeout 120 \
      --access-logfile - \
      --error-logfile -
else
    echo "Running custom command: $@"
    exec "$@"
fi
