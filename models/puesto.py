"""Modelo Puesto (puestos de los vendedores)."""
from db import consultar


def listar():
    return consultar(
        "SELECT pu.vendedor_id AS id, pu.nombre, pu.barrio, pu.ciudad, "
        "       pu.horario, pu.abierto, pu.acepta_domicilio, "
        "       pu.costo_domicilio, COUNT(p.id) AS n_productos "
        "FROM puesto pu "
        "JOIN usuario u ON u.id = pu.vendedor_id AND u.activo = 1 "
        "LEFT JOIN producto p "
        "       ON p.vendedor_id = pu.vendedor_id AND p.activo = 1 "
        "GROUP BY pu.vendedor_id "
        "ORDER BY pu.abierto DESC, pu.nombre"
    )


def obtener(puesto_id):
    return consultar(
        "SELECT pu.vendedor_id AS id, pu.nombre, pu.descripcion, "
        "       pu.direccion, pu.barrio, pu.ciudad, pu.horario, "
        "       pu.abierto, pu.acepta_domicilio, pu.costo_domicilio "
        "FROM puesto pu "
        "JOIN usuario u ON u.id = pu.vendedor_id AND u.activo = 1 "
        "WHERE pu.vendedor_id = %s",
        (puesto_id,),
        uno=True,
    )


def productos_de(puesto_id):
    return consultar(
        "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
        "       p.disponible, c.nombre AS categoria "
        "FROM producto p JOIN categoria c ON c.id = p.categoria_id "
        "WHERE p.vendedor_id = %s AND p.activo = 1 "
        "ORDER BY c.id, p.nombre",
        (puesto_id,),
    )


def para_mapa():
    return consultar(
        "SELECT pu.vendedor_id AS id, pu.nombre, pu.barrio, "
        "       pu.latitud, pu.longitud, pu.abierto "
        "FROM puesto pu "
        "JOIN usuario u ON u.id = pu.vendedor_id AND u.activo = 1 "
        "WHERE pu.latitud IS NOT NULL AND pu.longitud IS NOT NULL"
    )
