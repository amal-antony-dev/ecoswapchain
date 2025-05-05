#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


import requests
import jwt
import datetime
from decouple import Config, RepositoryEnv

NODE_API_URL = 'http://localhost:3000/ping/'

file_path = "/media/alastor/New Volume/EcoSwapChain/ESC-Backend/esc-server-mint/ecoswapchain/configure .env"
env_config = Config(RepositoryEnv(file_path))
key = env_config.get('JWT_SECRET')

def get_jwt_token():
    print(key)
    payload = {
        'client': 'django-app',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    return jwt.encode(payload, key, algorithm='HS256')

def fetch_node_data():
    token = get_jwt_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(NODE_API_URL, headers=headers)
    return response.json()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoswapchain.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    fetch_node_data()
    main()
