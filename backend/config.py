import os

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'qwer!234A',
    'database': 'student_management',
    'charset': 'utf8mb4',
    'cursorclass': None
}

SECRET_KEY = os.getenv('SECRET_KEY', 'school_manager_secret_key_2024')
JWT_EXPIRE_HOURS = 24