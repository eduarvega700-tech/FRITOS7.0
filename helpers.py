"""Utilidades generales: formato de precios, CSRF, slugs, carrito, fotos."""
import hmac
import json
import os
import re
import secrets
import unicodedata

from flask import abort, current_app, request, session

from models.pedido import MAX_UNIDADES


def formato_cop(valor):
    """2500 -> $2.500"""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def verificar_csrf():
    # Todo formulario POST debe traer el token oculto csrf_token.
    if request.method == "POST":
        enviado = (
            request.form.get("csrf_token", "")
            or request.headers.get("X-CSRF-Token", "")
        )
        esperado = session.get("csrf", "")
        if not esperado or not hmac.compare_digest(
            enviado.encode(), esperado.encode()
        ):
            abort(400)


def crear_slug(texto):
    base = unicodedata.normalize("NFKD", texto.lower())
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def quitar_imagen(ruta):
    """Borra una foto subida (solo dentro de static/uploads)."""
    if ruta and ruta.startswith("uploads/"):
        try:
            os.remove(os.path.join(current_app.static_folder, ruta))
        except OSError:
            pass


def leer_items(texto):
    """Convierte {"id": cantidad} (JSON) en {id:int -> cantidad:int} validado."""
    try:
        bruto = json.loads(texto or "{}")
    except (TypeError, ValueError):
        return {}
    if not isinstance(bruto, dict):
        return {}
    items = {}
    for clave, cantidad in bruto.items():
        try:
            producto_id, cantidad = int(clave), int(cantidad)
        except (TypeError, ValueError):
            continue
        if producto_id > 0 and cantidad > 0:
            items[producto_id] = min(cantidad, MAX_UNIDADES)
    return items
