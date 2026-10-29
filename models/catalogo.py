"""Modelo Catálogo: lo que ven los clientes (vista v_productos_activos)."""
from db import consultar
from models.datos_respaldo import CATEGORIAS, PRODUCTOS


def categorias():
    return consultar("SELECT nombre, slug, imagen FROM categoria ORDER BY id")


def productos_activos(slug=""):
    if slug:
        return consultar(
            "SELECT * FROM v_productos_activos WHERE categoria = %s ORDER BY id",
            (slug,),
        )
    return consultar("SELECT * FROM v_productos_activos ORDER BY id")


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
