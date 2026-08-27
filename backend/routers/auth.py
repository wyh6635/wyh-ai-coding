from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from datetime import datetime, timedelta
import json
import base64
import hashlib
import secrets

from database import query_one
from schemas.user import LoginRequest
from utils.captcha import generate_captcha, verify_captcha, encrypt_password, verify_password
from config import SECRET_KEY

router = APIRouter(prefix='/api/auth', tags=['认证接口'])

captcha_cache = {}


def make_response(code: int = 200, msg: str = 'success', data: dict = None):
    return JSONResponse(
        status_code=200,
        content={'code': code, 'msg': msg, 'data': data}
    )


@router.get('/captcha')
def get_captcha():
    img_base64, captcha_info = generate_captcha()
    captcha_key = captcha_info['key']
    captcha_code = captcha_info['code']
    captcha_cache[captcha_key] = {
        'code': captcha_code,
        'expire_at': datetime.now() + timedelta(minutes=5)
    }
    return make_response(data={
        'captcha_key': captcha_key,
        'captcha_img': f'data:image/png;base64,{img_base64}'
    })


@router.post('/login')
async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return make_response(code=400, msg='请求参数格式错误')

    try:
        login_data = LoginRequest(**body)
    except ValidationError as e:
        errors = []
        for err in e.errors():
            errors.append(err['msg'])
        return make_response(code=400, msg='; '.join(errors))

    captcha_key = login_data.captcha_key
    captcha_input = login_data.captcha

    if captcha_key not in captcha_cache:
        return make_response(code=400, msg='验证码已过期，请重新获取')

    captcha_info = captcha_cache[captcha_key]
    if datetime.now() > captcha_info['expire_at']:
        del captcha_cache[captcha_key]
        return make_response(code=400, msg='验证码已过期，请重新获取')

    if not verify_captcha(captcha_info['code'], captcha_input):
        del captcha_cache[captcha_key]
        return make_response(code=400, msg='验证码错误')

    del captcha_cache[captcha_key]

    user = query_one(
        "SELECT id, username, password, real_name, avatar, email, phone, role, status FROM user WHERE username = %s AND deleted = 0",
        (login_data.username,)
    )

    if not user:
        return make_response(code=400, msg='用户名或密码错误')

    if user['status'] != 1:
        return make_response(code=400, msg='账号已被禁用，请联系管理员')

    if not verify_password(login_data.password, user['password']):
        return make_response(code=400, msg='用户名或密码错误')

    token_data = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': (datetime.now() + timedelta(hours=24)).timestamp()
    }
    token_json = json.dumps(token_data)
    token = base64.b64encode(token_json.encode()).decode()
    token_hash = hashlib.sha256(f'{token}:{SECRET_KEY}'.encode()).hexdigest()
    full_token = f'{token}.{token_hash}'

    from database import execute
    execute(
        "UPDATE user SET last_login_time = %s WHERE id = %s",
        (datetime.now(), user['id'])
    )

    user_info = {
        'id': user['id'],
        'username': user['username'],
        'real_name': user.get('real_name'),
        'avatar': user.get('avatar'),
        'email': user.get('email'),
        'phone': user.get('phone'),
        'role': user['role'],
        'status': user['status']
    }

    return make_response(
        code=200,
        msg='登录成功',
        data={'token': full_token, 'user': user_info}
    )


@router.post('/logout')
async def logout(request: Request):
    return make_response(msg='退出登录成功')


@router.get('/user-info')
async def get_user_info(request: Request, authorization: str = None):
    if not authorization:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            authorization = auth_header[7:]

    if not authorization:
        return make_response(code=401, msg='未登录，请先登录')

    try:
        parts = authorization.split('.')
        if len(parts) < 2:
            return make_response(code=401, msg='Token格式错误')

        payload = parts[0]
        token_hash = parts[1]

        expected_hash = hashlib.sha256(f'{payload}:{SECRET_KEY}'.encode()).hexdigest()
        if token_hash != expected_hash:
            return make_response(code=401, msg='Token无效')

        token_data = json.loads(base64.b64decode(payload))
        if token_data.get('exp', 0) < datetime.now().timestamp():
            return make_response(code=401, msg='Token已过期')

        user = query_one(
            "SELECT id, username, real_name, avatar, email, phone, role, status FROM user WHERE id = %s AND deleted = 0",
            (token_data['user_id'],)
        )

        if not user:
            return make_response(code=401, msg='用户不存在')

        user_info = {
            'id': user['id'],
            'username': user['username'],
            'real_name': user.get('real_name'),
            'avatar': user.get('avatar'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'role': user['role'],
            'status': user['status']
        }

        return make_response(data=user_info)

    except Exception:
        return make_response(code=401, msg='Token解析失败')