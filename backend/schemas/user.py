from pydantic import BaseModel, field_validator
from typing import Optional
import re


class LoginRequest(BaseModel):
    username: str
    password: str
    captcha: str
    captcha_key: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError('密码不能为空')
        v = v.strip()
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v

    @field_validator('captcha')
    @classmethod
    def validate_captcha(cls, v):
        if not v or not v.strip():
            raise ValueError('验证码不能为空')
        return v.strip()

    @field_validator('captcha_key')
    @classmethod
    def validate_captcha_key(cls, v):
        if not v or not v.strip():
            raise ValueError('验证码标识不能为空')
        return v.strip()


class UserInfoResponse(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: int


class LoginResponse(BaseModel):
    token: str
    user: UserInfoResponse


class ApiResponse(BaseModel):
    code: int = 200
    msg: str = 'success'
    data: Optional[dict] = None