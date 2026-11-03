"""Modelo Venta: lo que los clientes le han comprado a un vendedor.

Une pedido_item con producto para quedarse solo con los ítems del vendedor.
Las ventas canceladas no cuentan en los totales.
"""
from db import consultar

VACIAS = {
    "productos": 0, "visibles": 0, "agotados": 0, "pendientes": 0,
    "pedidos": 0, "unidades": 0, "ingresos": 0, "promedio": 0,
}

# Ítems de pedidos que pertenecen a un vendedor (%(v)s = id del vendedor).
_ITEMS_DEL_VENDEDOR = (
    "FROM pedido p "
    "JOIN pedido_item i ON i.pedido_id = p.id "
    "JOIN producto pr ON pr.id = i.producto_id "
    "WHERE pr.vendedor_id = %(v)s "
)


def resumen(vendedor_id):
    """Cifras del panel del vendedor."""
    fila = consultar(
        "SELECT "
        " (SELECT COUNT(*) FROM producto WHERE vendedor_id = %(v)s) AS productos,"
        " (SELECT COUNT(*) FROM producto"
        "   WHERE vendedor_id = %(v)s AND activo = 1) AS visibles,"
        " (SELECT COUNT(*) FROM producto"
        "   WHERE vendedor_id = %(v)s AND disponible = 0) AS agotados,"
        " (SELECT COUNT(DISTINCT p.id) " + _ITEMS_DEL_VENDEDOR +
        "   AND p.estado IN ('pendiente', 'preparando')) AS pendientes,"
        " (SELECT COUNT(DISTINCT p.id) " + _ITEMS_DEL_VENDEDOR +
        "   AND p.estado <> 'cancelado') AS pedidos,"
        " (SELECT COALESCE(SUM(i.cantidad), 0) " + _ITEMS_DEL_VENDEDOR +
        "   AND p.estado <> 'cancelado') AS unidades,"
        " (SELECT COALESCE(SUM(i.precio_unitario * i.cantidad), 0) "
        + _ITEMS_DEL_VENDEDOR +
        "   AND p.estado <> 'cancelado') AS ingresos",
        {"v": vendedor_id},
        uno=True,
    )
    datos = {clave: int(valor or 0) for clave, valor in fila.items()}
    datos["promedio"] = (
        datos["ingresos"] // datos["pedidos"] if datos["pedidos"] else 0
    )
    return datos


def lista(vendedor_id, estado="", limite=None):
    """Pedidos que incluyen productos del vendedor (con su subtotal)."""
    sql = (
        "SELECT p.id, p.tipo_entrega, p.direccion, p.notas, p.estado, "
        "       p.creado_en, u.nombre AS cliente, "
        "       SUM(i.precio_unitario * i.cantidad) AS subtotal "
        "FROM pedido p "
        "JOIN usuario u ON u.id = p.cliente_id "
        "JOIN pedido_item i ON i.pedido_id = p.id "
        "JOIN producto pr ON pr.id = i.producto_id "
        "WHERE pr.vendedor_id = %s "
    )
    params = [vendedor_id]
    if estado:
        sql += "AND p.estado = %s "
        params.append(estado)
    sql += (
        "GROUP BY p.id, p.tipo_entrega, p.direccion, p.notas, "
        "         p.estado, p.creado_en, u.nombre "
        "ORDER BY p.id DESC"
    )
    if limite:
        sql += " LIMIT %s"
        params.append(limite)
    return consultar(sql, tuple(params))


def items(vendedor_id):
    """{pedido_id: [ítems del vendedor]} para mostrar el detalle."""
    filas = consultar(
        "SELECT i.pedido_id, i.nombre, i.precio_unitario, i.cantidad "
        "FROM pedido_item i "
        "JOIN producto pr ON pr.id = i.producto_id "
        "WHERE pr.vendedor_id = %s ORDER BY i.id",
        (vendedor_id,),
    )
    agrupados = {}
    for fila in filas:
        agrupados.setdefault(fila["pedido_id"], []).append(fila)
    return agrupados


def mas_vendidos(vendedor_id, limite=5):
    return consultar(
        "SELECT i.nombre, SUM(i.cantidad) AS unidades, "
        "       SUM(i.precio_unitario * i.cantidad) AS ingresos "
        "FROM pedido p "
        "JOIN pedido_item i ON i.pedido_id = p.id "
        "JOIN producto pr ON pr.id = i.producto_id "
        "WHERE pr.vendedor_id = %s AND p.estado <> 'cancelado' "
        "GROUP BY pr.id, i.nombre "
        "ORDER BY unidades DESC, ingresos DESC LIMIT %s",
        (vendedor_id, limite),
    )
