"""Carrito guardado en la BD (tablas carrito, carrito_item y vista v_carrito).

Se registra desde app.py con:  carrito_api.registrar(app)
Requiere haber ejecutado carrito.sql y explorar_carrito.sql.
"""
from flask import jsonify, request, session, url_for

import db

MAX_UNIDADES = 20  # usa el mismo valor que ya pasas a carrito.html como max_unidades


# ── Acceso a la BD ───────────────────────────────────────────────
# Busca en db.py la función que entrega la conexión. Si tu db.py usa otro
# nombre y sale el error "no encontré cómo db.py entrega la conexión",
# cambia el cuerpo de _conexion() por:   return db.TU_FUNCION()
def _conexion():
    for nombre in ("get_db", "get_conn", "get_connection", "get_conexion",
                   "conexion", "conectar", "obtener_conexion", "db_conn"):
        f = getattr(db, nombre, None)
        if callable(f):
            return f()
    raise RuntimeError("carrito_api: no encontré cómo db.py entrega la conexión; "
                       "edita _conexion() en views/carrito_api.py")


def _cursor(conn):
    try:
        return conn.cursor(dictionary=True)      # mysql-connector
    except TypeError:
        return conn.cursor()                     # pymysql (DictCursor o tuplas)


def _a_dicts(cur, filas):
    if filas and not isinstance(filas[0], dict):
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, f)) for f in filas]
    return list(filas)


def q_all(sql, args=()):
    cur = _cursor(_conexion())
    cur.execute(sql, args)
    filas = _a_dicts(cur, cur.fetchall())
    cur.close()
    return filas


def q_one(sql, args=()):
    filas = q_all(sql, args)
    return filas[0] if filas else None


def q_exec(sql, args=()):
    conn = _conexion()
    cur = _cursor(conn)
    cur.execute(sql, args)
    conn.commit()
    cur.close()


# ── Utilidades ───────────────────────────────────────────────────
def _uid():
    """Solo los clientes con sesión iniciada tienen carrito."""
    return session.get("usuario_id") if session.get("rol") == "cliente" else None


def _datos():
    """Acepta JSON o formulario (el formulario pasa tu verificar_csrf)."""
    d = request.get_json(silent=True)
    return d if isinstance(d, dict) else request.form


def _entero(valor, defecto=0):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return defecto


def _sin_sesion():
    return jsonify(error="login", login=url_for("acceso_rol", rol="cliente")), 401


def _unidades(uid):
    r = q_one("SELECT COALESCE(SUM(cantidad),0) AS n FROM carrito_item WHERE usuario_id=%s", (uid,))
    return int(r["n"])


# ── Rutas ────────────────────────────────────────────────────────
def api_carrito():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    filas = q_all("""SELECT producto_id, nombre, precio_unitario, cantidad, img, disponible
                     FROM v_carrito WHERE usuario_id=%s ORDER BY nombre""", (uid,))
    items, total, unidades = [], 0, 0
    for f in filas:
        precio = int(f["precio_unitario"])
        img = f["img"] if f["img"] and str(f["img"]).startswith("uploads/") else "img/default.png"
        items.append(dict(producto_id=f["producto_id"], nombre=f["nombre"], precio=precio,
                          cantidad=f["cantidad"], disponible=bool(f["disponible"]),
                          img=url_for("static", filename=img)))
        total += precio * f["cantidad"]
        unidades += f["cantidad"]
    cab = q_one("""SELECT c.vendedor_id AS id, pu.nombre FROM carrito c
                   LEFT JOIN puesto pu ON pu.vendedor_id = c.vendedor_id
                   WHERE c.usuario_id=%s""", (uid,))
    return jsonify(items=items, total=total, unidades=unidades,
                   puesto=(cab if cab and items else None))


def api_carrito_contador():
    uid = _uid()
    return jsonify(unidades=_unidades(uid) if uid else 0)


def api_carrito_agregar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    d = _datos()
    pid = _entero(d.get("producto_id"))
    cant = max(1, min(_entero(d.get("cantidad"), 1), MAX_UNIDADES))
    reemplazar = str(d.get("reemplazar", "")).lower() in ("1", "true")

    pr = q_one("""SELECT pr.id, pr.vendedor_id, pr.activo, pr.disponible, pu.abierto
                  FROM producto pr
                  LEFT JOIN puesto pu ON pu.vendedor_id = pr.vendedor_id
                  WHERE pr.id=%s""", (pid,))
    if not pr or not pr["activo"] or not pr["disponible"] or pr["vendedor_id"] is None:
        return jsonify(error="no_disponible"), 404
    if pr["abierto"] is None:                      # el vendedor aún no tiene puesto
        q_exec("""INSERT IGNORE INTO puesto (vendedor_id, nombre)
                  SELECT id, CONCAT('Puesto de ', nombre) FROM usuario WHERE id=%s""",
               (pr["vendedor_id"],))
    elif not pr["abierto"]:
        return jsonify(error="cerrado"), 409

    # El carrito es de un solo puesto
    actual = q_one("SELECT vendedor_id FROM carrito WHERE usuario_id=%s", (uid,))
    if actual and actual["vendedor_id"] != pr["vendedor_id"] and _unidades(uid) > 0:
        if not reemplazar:
            return jsonify(error="otro_puesto"), 409
        q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (uid,))

    q_exec("""INSERT INTO carrito (usuario_id, vendedor_id) VALUES (%s,%s)
              ON DUPLICATE KEY UPDATE vendedor_id = VALUES(vendedor_id)""",
           (uid, pr["vendedor_id"]))
    q_exec("""INSERT INTO carrito_item (usuario_id, producto_id, cantidad) VALUES (%s,%s,%s)
              ON DUPLICATE KEY UPDATE cantidad = LEAST(cantidad + VALUES(cantidad), %s)""",
           (uid, pid, cant, MAX_UNIDADES))
    return jsonify(ok=True, unidades=_unidades(uid))


def api_carrito_cantidad():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    d = _datos()
    pid, delta = _entero(d.get("producto_id")), _entero(d.get("delta"))
    it = q_one("SELECT cantidad FROM carrito_item WHERE usuario_id=%s AND producto_id=%s", (uid, pid))
    if not it:
        return jsonify(error="no_existe"), 404
    nueva = min(MAX_UNIDADES, it["cantidad"] + delta)
    if nueva <= 0:
        q_exec("DELETE FROM carrito_item WHERE usuario_id=%s AND producto_id=%s", (uid, pid))
    else:
        q_exec("UPDATE carrito_item SET cantidad=%s WHERE usuario_id=%s AND producto_id=%s",
               (nueva, uid, pid))
    return jsonify(ok=True, unidades=_unidades(uid))


def api_carrito_quitar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    q_exec("DELETE FROM carrito_item WHERE usuario_id=%s AND producto_id=%s",
           (uid, _entero(_datos().get("producto_id"))))
    return jsonify(ok=True, unidades=_unidades(uid))


def api_carrito_vaciar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (uid,))
    return jsonify(ok=True, unidades=0)


def vaciar_carrito(uid):
    """Llámala desde pedido_nuevo cuando el pedido se guarde bien."""
    q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (uid,))


def registrar(app):
    reglas = [
        ("/api/mi-carrito",           api_carrito,            ["GET"]),
        ("/api/mi-carrito/contador",  api_carrito_contador,   ["GET"]),
        ("/api/mi-carrito/agregar",   api_carrito_agregar,    ["POST"]),
        ("/api/mi-carrito/cantidad",  api_carrito_cantidad,   ["POST"]),
        ("/api/mi-carrito/quitar",    api_carrito_quitar,     ["POST"]),
        ("/api/mi-carrito/vaciar",    api_carrito_vaciar,     ["POST"]),
    ]
    for ruta, vista, metodos in reglas:
        app.add_url_rule(ruta, endpoint="micarrito_" + vista.__name__, view_func=vista, methods=metodos)
