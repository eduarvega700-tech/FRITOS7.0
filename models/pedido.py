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


def crear(cliente_id, tipo, direccion, notas, items):
    """Crea pedido con precios vigentes y descuenta inventario en una transacción."""
    if not items:
        raise ValueError("Tu carrito está vacío.")
    db = get_db()
    db.begin()
    try:
        ids = list(items)
        marcas = ",".join(["%s"] * len(ids))
        with db.cursor() as cur:
            cur.execute(
                "SELECT p.id,p.nombre,p.precio,p.cantidad_disponible,p.activo,p.oferta_activa,"
                "p.descuento_porcentaje,u.activo AS vendedor_activo "
                "FROM producto p JOIN usuario u ON u.id=p.vendedor_id "
                "WHERE p.id IN (" + marcas + ") FOR UPDATE", tuple(ids)
            )
            filas = cur.fetchall()
            por_id = {f["id"]: f for f in filas}
            if len(por_id) != len(items):
                raise ValueError("Uno de los productos ya no está disponible. Actualiza tu carrito.")
            total = 0
            lineas = []
            for producto_id, cantidad in items.items():
                f = por_id[producto_id]
                if not f["activo"] or not f["vendedor_activo"]:
                    raise ValueError(f"{f['nombre']} ya no está disponible.")
                if cantidad > int(f["cantidad_disponible"]):
                    raise ValueError(f"Solo quedan {f['cantidad_disponible']} unidades de {f['nombre']}.")
                precio = int(f["precio"])
                if f["oferta_activa"]:
                    precio = precio * (100 - int(f["descuento_porcentaje"])) // 100
                total += precio * cantidad
                lineas.append((producto_id, f["nombre"], precio, cantidad))

            cur.execute(
                "INSERT INTO pedido (cliente_id,tipo_entrega,direccion,notas,total) "
                "VALUES (%s,%s,%s,%s,%s)",
                (cliente_id,tipo,direccion if tipo == "domicilio" else None,notas or None,total),
            )
            pedido_id = cur.lastrowid
            for producto_id, nombre, precio, cantidad in lineas:
                cur.execute(
                    "INSERT INTO pedido_item (pedido_id,producto_id,nombre,precio_unitario,cantidad) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (pedido_id,producto_id,nombre,precio,cantidad),
                )
                cur.execute(
                    "UPDATE producto SET cantidad_disponible=cantidad_disponible-%s, "
                    "disponible=(cantidad_disponible-%s > 0) WHERE id=%s",
                    (cantidad,cantidad,producto_id),
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
    """Actualiza estado; al cancelar por primera vez devuelve unidades al inventario."""
    db = get_db()
    db.begin()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT estado FROM pedido WHERE id=%s FOR UPDATE", (pedido_id,))
            actual = cur.fetchone()
            if actual is None:
                db.rollback()
                return False
            if actual["estado"] == estado:
                db.commit()
                return True
            # Un pedido cancelado no se reactiva para evitar descontar stock dos veces.
            if actual["estado"] == "cancelado":
                db.rollback()
                return False
            if estado == "cancelado":
                cur.execute("SELECT producto_id,cantidad FROM pedido_item WHERE pedido_id=%s", (pedido_id,))
                for item in cur.fetchall():
                    if item["producto_id"] is not None:
                        cur.execute(
                            "UPDATE producto SET cantidad_disponible=cantidad_disponible+%s,disponible=1 "
                            "WHERE id=%s", (item["cantidad"],item["producto_id"])
                        )
            cur.execute("UPDATE pedido SET estado=%s WHERE id=%s", (estado,pedido_id))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
