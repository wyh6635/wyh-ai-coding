import hashlib
import secrets
import io
import base64
from PIL import Image, ImageDraw, ImageFont


def generate_captcha(width: int = 120, height: int = 40) -> tuple:
    key = secrets.token_hex(16)
    code = secrets.token_hex(3)[:4].upper()
    img = Image.new('RGB', (width, height), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
    except Exception:
        font = ImageFont.load_default()
    for i, char in enumerate(code):
        x = 15 + i * 25
        y = 5 + secrets.randbelow(5)
        color = (
            secrets.randbelow(100) + 155,
            secrets.randbelow(100) + 100,
            secrets.randbelow(100) + 155
        )
        draw.text((x, y), char, fill=color, font=font)
    for i in range(5):
        x1 = secrets.randbelow(width)
        y1 = secrets.randbelow(height)
        x2 = secrets.randbelow(width)
        y2 = secrets.randbelow(height)
        draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 150), width=1)
    for i in range(30):
        x = secrets.randbelow(width)
        y = secrets.randbelow(height)
        draw.point((x, y), fill=(150, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    captcha_store = {'key': key, 'code': code}
    return img_base64, captcha_store


def verify_captcha(stored_code: str, input_code: str) -> bool:
    if not stored_code or not input_code:
        return False
    return stored_code.upper() == input_code.upper()


def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, encrypted: str) -> bool:
    return encrypt_password(password) == encrypted