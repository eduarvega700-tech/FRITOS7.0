"""Configuración de FRITOS TECH."""
import os

from pymysql.cursors import DictCursor

EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-en-produccion")

    # Datos de conexión a MySQL (variables de entorno o valores por defecto).
    MYSQL = {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DB", "fritos_tech"),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True,
    }

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB por foto
