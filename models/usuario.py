"""Modelo Usuario: tabla usuario e historial_acceso."""
from db import consultar, ejecutar

_COLUMNAS_LISTA = "id, nombre, correo, rol, activo, creado_en, ultimo_acceso"


def buscar_para_login(correo, rol):
    return consultar(
        "SELECT id, nombre, correo, clave_hash, rol "
        "FROM usuario WHERE correo = %s AND rol = %s AND activo = 1",
        (correo, rol),
        uno=True,
    )


def registrar_acceso(usuario_id, ip):
    ejecutar("UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s", (usuario_id,))
    ejecutar(
        "INSERT INTO historial_acceso (usuario_id, ip) VALUES (%s, %s)",
        (usuario_id, ip),
    )


def crear(nombre, correo, clave_hash, rol):
    return ejecutar(
        "INSERT INTO usuario (nombre, correo, clave_hash, rol) VALUES (%s, %s, %s, %s)",
        (nombre, correo, clave_hash, rol),
    )


def crear_o_actualizar_admin(nombre, correo, clave_hash):
    return ejecutar(
        "INSERT INTO usuario (nombre, correo, clave_hash, rol) "
        "VALUES (%s, %s, %s, 'administrador') "
        "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), "
        "clave_hash = VALUES(clave_hash), rol = 'administrador', activo = 1",
        (nombre, correo, clave_hash),
    )


def listar(rol=""):
    base = f"SELECT {_COLUMNAS_LISTA} FROM usuario "
    if rol:
        return consultar(base + "WHERE rol = %s ORDER BY id DESC", (rol,))
    return consultar(base + "ORDER BY id DESC")


def recientes(limite=6):
    return consultar(
        "SELECT nombre, correo, rol, activo, creado_en "
        "FROM usuario ORDER BY id DESC LIMIT %s",
        (limite,),
    )


def alternar_activo(usuario_id):
    """Activa/desactiva una cuenta. Devuelve las filas afectadas."""
    return ejecutar(
        "UPDATE usuario SET activo = 1 - activo WHERE id = %s", (usuario_id,)
    )
