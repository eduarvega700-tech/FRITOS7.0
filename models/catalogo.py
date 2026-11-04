"""Modelo Catálogo: lo que ven los clientes (vista v_productos_activos)."""
from db import consultar
from models.datos_respaldo import CATEGORIAS, PRODUCTOS


def categorias():
    return consultar("SELECT nombre, slug, imagen FROM categoria ORDER BY id")


def productos_activos(slug=""):
    # Se une con la tabla producto para traer también la descripción
    # sin depender de las columnas que tenga la vista v_productos_activos.
    base = (
        "SELECT v.*, p.descripcion "
        "FROM v_productos_activos v JOIN producto p ON p.id = v.id "
    )
    if slug:
        return consultar(
            base + "WHERE v.categoria = %s ORDER BY v.id",
            (slug,),
        )
    return consultar(base + "ORDER BY v.id")


def productos_por_ids(ids):
    """Productos visibles para los ids dados."""
    if not ids:
        return []
    marcas = ",".join(["%s"] * len(ids))
    return consultar(
        "SELECT id, nombre, vendedor, precio, img "
        "FROM v_productos_activos WHERE id IN (" + marcas + ")",
        tuple(ids),
    )


def respaldo(slug=""):
    """Datos de ejemplo por si MySQL no responde."""
    productos = [p for p in PRODUCTOS if not slug or p["categoria"] == slug]
    return CATEGORIAS, productos
