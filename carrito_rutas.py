# ───────────────────────────────────────────────────────────────
#  Rutas del carrito guardado en la BD (carrito + carrito_item)
#  Pégalas en app.py DESPUÉS de crear `app` y tus helpers de BD.
#  Requiere haber ejecutado carrito.sql (tablas carrito, carrito_item, vista v_carrito).
# ───────────────────────────────────────────────────────────────
from flask import jsonify, request, session, url_for

MAX_UNIDADES = 20          # usa el mismo valor que ya pasas a carrito.html


# ── Helpers de BD: ADÁPTALOS a como ya consultas tu base ──────────
# Deben devolver dicts. Ejemplo con pymysql:
#   def q_all(sql, args=()):
#       with get_db().cursor() as c: c.execute(sql, args); return c.fetchall()
#   def q_one(sql, args=()):
#       with get_db().cursor() as c: c.execute(sql, args); return c.fetchone()
#   def q_exec(sql, args=()):
#       db = get_db()
#       with db.cursor() as c: c.execute(sql, args)
#       db.commit()
# (q_all, q_one y q_exec se asumen definidos)


def _uid():
    """Solo los clientes con sesión iniciada tienen carrito."""
    return session.get('usuario_id') if session.get('rol') == 'cliente' else None


def _total_unidades(uid):
    r = q_one("SELECT COALESCE(SUM(cantidad),0) AS n FROM carrito_item WHERE usuario_id=%s", (uid,))
    return int(r['n'])


def _sin_sesion():
    return jsonify(error='login', login=url_for('acceso_rol', rol='cliente')), 401


@app.get('/api/carrito')
def api_carrito():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    filas = q_all("""SELECT producto_id, nombre, precio_unitario, cantidad, img, disponible
                     FROM v_carrito WHERE usuario_id=%s ORDER BY nombre""", (uid,))
    items, total, unidades = [], 0, 0
    for f in filas:
        precio = int(f['precio_unitario'])
        img = f['img'] if f['img'] and f['img'].startswith('uploads/') else 'img/default.png'
        items.append(dict(producto_id=f['producto_id'], nombre=f['nombre'], precio=precio,
                          cantidad=f['cantidad'], disponible=bool(f['disponible']),
                          img=url_for('static', filename=img)))
        total += precio * f['cantidad']
        unidades += f['cantidad']
    cab = q_one("""SELECT c.vendedor_id, pu.nombre FROM carrito c
                   LEFT JOIN puesto pu ON pu.vendedor_id = c.vendedor_id
                   WHERE c.usuario_id=%s""", (uid,))
    return jsonify(items=items, total=total, unidades=unidades,
                   puesto=({'id': cab['vendedor_id'], 'nombre': cab['nombre']} if cab and items else None))


@app.get('/api/carrito/contador')
def api_carrito_contador():
    uid = _uid()
    return jsonify(unidades=_total_unidades(uid) if uid else 0)


@app.post('/api/carrito/agregar')
def api_carrito_agregar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    d = request.get_json(silent=True) or {}
    try:
        pid = int(d.get('producto_id', 0))
        cant = max(1, min(int(d.get('cantidad', 1)), MAX_UNIDADES))
    except (TypeError, ValueError):
        return jsonify(error='datos'), 400

    pr = q_one("""SELECT pr.id, pr.vendedor_id, pr.activo, pr.disponible, pu.abierto
                  FROM producto pr JOIN puesto pu ON pu.vendedor_id = pr.vendedor_id
                  WHERE pr.id=%s""", (pid,))
    if not pr or not pr['activo'] or not pr['disponible']:
        return jsonify(error='no_disponible'), 404
    if not pr['abierto']:
        return jsonify(error='cerrado'), 409

    # El carrito es de un solo puesto
    actual = q_one("SELECT vendedor_id FROM carrito WHERE usuario_id=%s", (uid,))
    if actual and actual['vendedor_id'] != pr['vendedor_id'] and _total_unidades(uid) > 0:
        if not d.get('reemplazar'):
            return jsonify(error='otro_puesto'), 409
        q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (uid,))

    q_exec("""INSERT INTO carrito (usuario_id, vendedor_id) VALUES (%s,%s)
              ON DUPLICATE KEY UPDATE vendedor_id = VALUES(vendedor_id)""", (uid, pr['vendedor_id']))
    q_exec("""INSERT INTO carrito_item (usuario_id, producto_id, cantidad) VALUES (%s,%s,%s)
              ON DUPLICATE KEY UPDATE cantidad = LEAST(cantidad + VALUES(cantidad), %s)""",
           (uid, pid, cant, MAX_UNIDADES))
    return jsonify(ok=True, unidades=_total_unidades(uid))


@app.post('/api/carrito/cantidad')
def api_carrito_cantidad():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    d = request.get_json(silent=True) or {}
    try:
        pid, delta = int(d.get('producto_id', 0)), int(d.get('delta', 0))
    except (TypeError, ValueError):
        return jsonify(error='datos'), 400
    it = q_one("SELECT cantidad FROM carrito_item WHERE usuario_id=%s AND producto_id=%s", (uid, pid))
    if not it:
        return jsonify(error='no_existe'), 404
    nueva = min(MAX_UNIDADES, it['cantidad'] + delta)
    if nueva <= 0:
        q_exec("DELETE FROM carrito_item WHERE usuario_id=%s AND producto_id=%s", (uid, pid))
    else:
        q_exec("UPDATE carrito_item SET cantidad=%s WHERE usuario_id=%s AND producto_id=%s", (nueva, uid, pid))
    return jsonify(ok=True, unidades=_total_unidades(uid))


@app.post('/api/carrito/quitar')
def api_carrito_quitar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    d = request.get_json(silent=True) or {}
    q_exec("DELETE FROM carrito_item WHERE usuario_id=%s AND producto_id=%s",
           (uid, int(d.get('producto_id', 0))))
    return jsonify(ok=True, unidades=_total_unidades(uid))


@app.post('/api/carrito/vaciar')
def api_carrito_vaciar():
    uid = _uid()
    if not uid:
        return _sin_sesion()
    q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (uid,))
    return jsonify(ok=True, unidades=0)


# En tu ruta pedido_nuevo, cuando el pedido se guarde bien, vacía el carrito:
#   q_exec("DELETE FROM carrito_item WHERE usuario_id=%s", (session['usuario_id'],))
# y lee los precios desde producto (no confíes en el navegador).
