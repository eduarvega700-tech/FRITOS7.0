"""Modelo Categoría (gestión del administrador)."""
from db import consultar, ejecutar


def opciones():
    return consultar("SELECT id, nombre FROM categoria ORDER BY id")


def listar_con_conteo():
    return consultar(
        "SELECT c.id, c.nombre, c.slug, COUNT(p.id) AS productos "
        "FROM categoria c LEFT JOIN producto p ON p.categoria_id = c.id "
        "GROUP BY c.id, c.nombre, c.slug ORDER BY c.id"
    )


def crear(nombre, slug):
    return ejecutar(
        "INSERT INTO categoria (nombre, slug) VALUES (%s, %s)", (nombre, slug)
    )


def eliminar(categoria_id):
    """Devuelve filas afectadas. Lanza IntegrityError si tiene productos."""
    return ejecutar("DELETE FROM categoria WHERE id = %s", (categoria_id,))
