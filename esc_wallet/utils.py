import jwt
from datetime import datetime, timedelta, timezone
from ecoswapchain.settings import BLOCK_SECRET

def get_jwt_token():
    payload = {
        'client': 'django-app',
        'exp': datetime.now(timezone.utc) + timedelta(days=5)
    }
    # In Django, modify get_jwt_token():
    return jwt.encode(payload, BLOCK_SECRET.encode('utf-8'), algorithm='HS256')