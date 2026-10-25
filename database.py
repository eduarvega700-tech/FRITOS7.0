
from flask import current_app, g
import pymysql
from pymysql.cursors import DictCursor


def get_db():
    """Obtiene o reutiliza la conexión MySQL de la petición actual."""
    if "db" not in g:
        g.db = pymysql.connect(
            **current_app.config["MYSQL"]
        )

    return g.db


def cerrar_db(error=None):
    """Cierra la conexión al terminar la petición."""
    conexion = g.pop("db", None)

    if conexion is not None:
        conexion.close()


def consultar(sql, params=(), uno=False):
    """Ejecuta una consulta y devuelve resultados como diccionarios."""
    conexion = get_db()

    with conexion.cursor() as cursor:
        cursor.execute(sql, params)

        if uno:
            return cursor.fetchone()

        return cursor.fetchall()


def ejecutar(sql, params=()):
    """Ejecuta una operación de escritura en la base de datos."""
    conexion = get_db()

    with conexion.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount
