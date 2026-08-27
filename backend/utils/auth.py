from fastapi import HTTPException, Request
import json
import base64
import hashlib
from datetime import datetime
from config import SECRET_KEY


async def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='未登录')

    token = auth_header[7:]
    try:
        parts = token.split('.')
        if len(parts) < 2:
            raise HTTPException(status_code=401, detail='Token格式错误')

        payload = parts[0]
        token_hash = parts[1]

        expected_hash = hashlib.sha256(f'{payload}:{SECRET_KEY}'.encode()).hexdigest()
        if token_hash != expected_hash:
            raise HTTPException(status_code=401, detail='Token无效')

        token_data = json.loads(base64.b64decode(payload))
        if token_data.get('exp', 0) < datetime.now().timestamp():
            raise HTTPException(status_code=401, detail='Token已过期')

        return token_data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail='Token解析失败')