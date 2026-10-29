"""Modelo Producto (vendedor y administrador).

Si se pasa vendedor_id, la operación solo afecta productos de ese vendedor.
"""
from db import consultar, ejecutar


def de_vendedor(vendedor_id):
    return consultar(
        "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
        "       p.activo, p.creado_en, c.nombre AS categoria "
        "FROM producto p JOIN categoria c ON c.id = p.categoria_id "
        "WHERE p.vendedor_id = %s "
        "ORDER BY p.creado_en DESC, p.id DESC",
        (vendedor_id,),
    )


def crear(vendedor_id, categoria_id, nombre, descripcion, precio, imagen):
    return ejecutar(
        "INSERT INTO producto "
        "(vendedor_id, categoria_id, nombre, descripcion, precio, imagen) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (vendedor_id, categoria_id, nombre, descripcion, precio, imagen),
    )


def alternar_activo(producto_id, vendedor_id=None):
    sql = "UPDATE producto SET activo = 1 - activo WHERE id = %s"
    params = (producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id = %s"
        params += (vendedor_id,)
    return ejecutar(sql, params)


def imagen_de(producto_id, vendedor_id=None):
    """Devuelve {'imagen': ...} o None si no existe."""
    sql = "SELECT imagen FROM producto WHERE id = %s"
    params = (producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id = %s"
        params += (vendedor_id,)
    return consultar(sql, params, uno=True)


def eliminar(producto_id, vendedor_id=None):
    sql = "DELETE FROM producto WHERE id = %s"
    params = (producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id = %s"
        params += (vendedor_id,)
    return ejecutar(sql, params)


def listar_todos():
    return consultar(
        "SELECT p.id, p.nombre, p.precio, p.activo, p.imagen, p.creado_en, "
        "       u.nombre AS vendedor, c.nombre AS categoria "
        "FROM producto p "
        "JOIN usuario u ON u.id = p.vendedor_id "
        "JOIN categoria c ON c.id = p.categoria_id "
        "ORDER BY p.id DESC"
    )


def recientes(limite=6):
    return consultar(
        "SELECT p.nombre, u.nombre AS vendedor, c.nombre AS categoria, "
        "       p.precio, p.activo "
        "FROM producto p "
        "JOIN usuario u ON u.id = p.vendedor_id "
        "JOIN categoria c ON c.id = p.categoria_id "
        "ORDER BY p.id DESC LIMIT %s",
        (limite,),
    )
