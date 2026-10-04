import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "yamanote.proxy.rlwy.net")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "13899"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "oCbVPTRnszcPLtrjBzhakQbRBaNyKaega")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "campusgo")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Moviles2026**01$")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
