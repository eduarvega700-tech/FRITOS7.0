"""Modelo Catálogo: productos visibles para los clientes."""
from db import consultar
from models.datos_respaldo import CATEGORIAS, PRODUCTOS


def categorias():
    return consultar("SELECT nombre,slug,imagen FROM categoria ORDER BY id")


def productos_activos(slug=""):
    base = ("SELECT v.*,p.descripcion,p.cantidad_disponible,p.oferta_activa,"
            "p.descuento_porcentaje,"
            "CASE WHEN p.oferta_activa=1 THEN FLOOR(p.precio*(100-p.descuento_porcentaje)/100) "
            "ELSE p.precio END AS precio_final "
            "FROM v_productos_activos v JOIN producto p ON p.id=v.id ")
    if slug:
        return consultar(base+"WHERE v.categoria=%s ORDER BY v.id",(slug,))
    return consultar(base+"ORDER BY v.id")


def productos_por_ids(ids):
    if not ids: return []
    marcas=",".join(["%s"]*len(ids))
    return consultar(
        "SELECT v.id,v.nombre,v.vendedor,v.precio,v.img,p.cantidad_disponible,p.oferta_activa,"
        "p.descuento_porcentaje,CASE WHEN p.oferta_activa=1 THEN FLOOR(v.precio*(100-p.descuento_porcentaje)/100) "
        "ELSE v.precio END AS precio_final FROM v_productos_activos v "
        "JOIN producto p ON p.id=v.id WHERE v.id IN ("+marcas+")",tuple(ids))


def respaldo(slug=""):
    productos=[p for p in PRODUCTOS if not slug or p["categoria"]==slug]
    return CATEGORIAS,productos
