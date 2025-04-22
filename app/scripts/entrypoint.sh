#!/bin/sh

if [ ! -f /data/initialized ]; then
    alembic upgrade head
    python scripts/create_default_users.py
    touch /data/initialized
    echo 'Default users have been initialized'
else
    echo 'Default users are already initialized'
fi

exec "$@"