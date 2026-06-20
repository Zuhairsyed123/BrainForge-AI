#!/usr/bin/env bash
# Exit on first error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
