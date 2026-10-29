"""Vistas del carrito y de los pedidos del cliente."""
import json

import pymysql
from flask import (current_app, flash, jsonify, redirect, render_template,
                   request, session, url_for)

from decoradores import cliente_requerido
from helpers import leer_items
from imagenes import ruta_imagen
from models import catalogo
from models import pedido as pedido_model


def carrito():
    # El contenido vive en el navegador; main.js lo dibuja pidiendo los datos
    # reales (precios, fotos) a /api/carrito.
    if session.get("rol") == "administrador":
        return redirect(url_for("admin_dashboard"))
    return render_template("carrito.html", max_unidades=pedido_model.MAX_UNIDADES)


def api_carrito():
    datos = request.get_json(silent=True) or {}
    items = leer_items(json.dumps(datos.get("items", {})))
    try:
        filas = catalogo.productos_por_ids(list(items))
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        return jsonify({"error": "db"}), 503

    productos = [{
        "id": f["id"],
        "nombre": f["nombre"],
        "vendedor": f["vendedor"],
        "precio": int(f["precio"]),
        "cantidad": items[f["id"]],
        "img": url_for("static", filename=ruta_imagen(f["nombre"], f["img"])),
    } for f in filas]
    return jsonify({"productos": productos})


@cliente_requerido
def pedido_nuevo():
    items = leer_items(request.form.get("items", ""))
    tipo = request.form.get("tipo_entrega", "")
    direccion = request.form.get("direccion", "").strip()
    notas = request.form.get("notas", "").strip()

    if not items:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("carrito"))
    if tipo not in pedido_model.TIPOS_ENTREGA:
        flash("Elige si quieres recoger o recibir a domicilio.", "danger")
        return redirect(url_for("carrito"))
    if tipo == "domicilio" and len(direccion) < 6:
        flash("Escribe la dirección de entrega.", "danger")
        return redirect(url_for("carrito"))
    if len(direccion) > 200 or len(notas) > 255:
        flash("La dirección o las notas son demasiado largas.", "danger")
        return redirect(url_for("carrito"))

    try:
        filas = catalogo.productos_por_ids(list(items))
        if len(filas) != len(items):
            flash("Algún producto ya no está disponible. Revisa tu carrito.", "warning")
            return redirect(url_for("carrito"))
        pedido_id = pedido_model.crear(
            session["usuario_id"], tipo, direccion, notas, filas, items
        )
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos registrar tu pedido. Inténtalo de nuevo.", "danger")
        return redirect(url_for("carrito"))

    flash(f"¡Pedido #{pedido_id} recibido! Te avisaremos cuando avance.", "success")
    # vaciar=1 le dice a main.js que limpie el carrito del navegador.
    return redirect(url_for("mis_pedidos", vaciar=1))


@cliente_requerido
def mis_pedidos():
    pedidos, items = [], {}
    try:
        pedidos, items = pedido_model.de_cliente(session["usuario_id"])
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar tus pedidos.", "danger")
    return render_template(
        "mis_pedidos.html", pedidos=pedidos, items=items,
        vaciar=request.args.get("vaciar") == "1",
    )
