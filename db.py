"""Conexión a MySQL: una conexión por petición."""
import pymysql
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(**current_app.config["MYSQL"])
    return g.db


def cerrar_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(cerrar_db)


def consultar(sql, params=(), uno=False):
    """SELECT: devuelve una fila (uno=True) o una lista de filas."""
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if uno else cur.fetchall()


def ejecutar(sql, params=()):
    """INSERT / UPDATE / DELETE: devuelve las filas afectadas."""
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount
