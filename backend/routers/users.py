from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from typing import Optional
from database import query_one, execute
from utils.response import make_response
from utils.auth import get_current_user
from utils.captcha import encrypt_password, verify_password

router = APIRouter(prefix='/api/users', tags=['用户管理'])


class PasswordChange(BaseModel):
    old_password: str
    new_password: str

    @field_validator('old_password', 'new_password')
    @classmethod
    def validate_password(cls, v, info):
        if not v or not v.strip():
            raise ValueError(f'{info.field_name}不能为空')
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v


class ProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None and v and '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None and v and len(v) != 11:
            raise ValueError('手机号格式不正确')
        return v


@router.get('/profile')
def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    user = query_one("""
        SELECT id, username, real_name, avatar, email, phone, role, status
        FROM user WHERE id = %s AND deleted = 0
    """, (user_id,))
    if not user:
        return make_response(code=404, msg='用户不存在')
    return make_response(data=user)


@router.put('/profile')
def update_profile(data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    user = query_one("SELECT id FROM user WHERE id = %s AND deleted = 0", (user_id,))
    if not user:
        return make_response(code=404, msg='用户不存在')

    updates = []
    params = []
    if data.real_name is not None:
        updates.append("real_name = %s")
        params.append(data.real_name)
    if data.email is not None:
        updates.append("email = %s")
        params.append(data.email)
    if data.phone is not None:
        updates.append("phone = %s")
        params.append(data.phone)

    if not updates:
        return make_response(msg='没有需要更新的字段')

    sql = f"UPDATE user SET {', '.join(updates)} WHERE id = %s"
    params.append(user_id)
    execute(sql, tuple(params))

    updated = query_one("SELECT id, username, real_name, email, phone, role FROM user WHERE id = %s", (user_id,))
    return make_response(msg='更新成功', data=updated)


@router.post('/change-password')
def change_password(data: PasswordChange, current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    user = query_one("SELECT password FROM user WHERE id = %s", (user_id,))
    if not user:
        return make_response(code=400, msg='用户不存在')

    if not verify_password(data.old_password, user['password']):
        return make_response(code=400, msg='原密码错误')

    new_encrypted = encrypt_password(data.new_password)
    execute("UPDATE user SET password = %s WHERE id = %s", (new_encrypted, user_id))
    return make_response(msg='密码修改成功')