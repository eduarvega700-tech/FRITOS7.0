"""Modelo Pedido (pedido y pedido_item)."""
from db import consultar, ejecutar, get_db

MAX_UNIDADES = 50  # máximo por producto en un pedido
ESTADOS_PEDIDO = ["pendiente", "preparando", "listo", "entregado", "cancelado"]
TIPOS_ENTREGA = ["recoger", "domicilio"]


def _agrupar_items(filas):
    items = {}
    for it in filas:
        items.setdefault(it["pedido_id"], []).append(it)
    return items


def crear(cliente_id, tipo, direccion, notas, productos, items):
    """Crea el pedido y sus ítems en una transacción. Devuelve el id.

    `productos` son las filas reales de MySQL; el precio SIEMPRE sale de ahí,
    nunca del navegador. `items` es {producto_id: cantidad}.
    """
    total = sum(int(f["precio"]) * items[f["id"]] for f in productos)
    db = get_db()
    db.begin()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO pedido "
                "(cliente_id, tipo_entrega, direccion, notas, total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (cliente_id, tipo,
                 direccion if tipo == "domicilio" else None,
                 notas or None, total),
            )
            pedido_id = cur.lastrowid
            for f in productos:
                cur.execute(
                    "INSERT INTO pedido_item "
                    "(pedido_id, producto_id, nombre, precio_unitario, cantidad) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (pedido_id, f["id"], f["nombre"],
                     int(f["precio"]), items[f["id"]]),
                )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return pedido_id


def de_cliente(cliente_id):
    """Devuelve (pedidos, items_por_pedido) del cliente."""
    pedidos = consultar(
        "SELECT id, tipo_entrega, direccion, notas, total, estado, creado_en "
        "FROM pedido WHERE cliente_id = %s ORDER BY id DESC",
        (cliente_id,),
    )
    filas = consultar(
        "SELECT i.pedido_id, i.nombre, i.precio_unitario, i.cantidad "
        "FROM pedido_item i JOIN pedido p ON p.id = i.pedido_id "
        "WHERE p.cliente_id = %s ORDER BY i.id",
        (cliente_id,),
    )
    return pedidos, _agrupar_items(filas)


def todos(estado=""):
    """Devuelve (pedidos, items_por_pedido) para el administrador."""
    base = (
        "SELECT p.id, p.tipo_entrega, p.direccion, p.notas, p.total, "
        "       p.estado, p.creado_en, u.nombre AS cliente, u.correo "
        "FROM pedido p JOIN usuario u ON u.id = p.cliente_id "
    )
    if estado:
        pedidos = consultar(base + "WHERE p.estado = %s ORDER BY p.id DESC", (estado,))
    else:
        pedidos = consultar(base + "ORDER BY p.id DESC")
    filas = consultar(
        "SELECT pedido_id, nombre, precio_unitario, cantidad "
        "FROM pedido_item ORDER BY id"
    )
    return pedidos, _agrupar_items(filas)


def recientes(limite=6):
    return consultar(
        "SELECT p.id, u.nombre AS cliente, p.total, p.estado, p.creado_en "
        "FROM pedido p JOIN usuario u ON u.id = p.cliente_id "
        "ORDER BY p.id DESC LIMIT %s",
        (limite,),
    )


def cambiar_estado(pedido_id, estado):
    """True si el pedido existe (rowcount 0 también pasa si el estado era igual)."""
    if ejecutar("UPDATE pedido SET estado = %s WHERE id = %s", (estado, pedido_id)):
        return True
    return consultar("SELECT id FROM pedido WHERE id = %s", (pedido_id,), uno=True) is not None
