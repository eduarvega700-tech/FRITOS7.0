"""Vistas públicas: inicio, explorar, puestos, mapa y páginas pendientes."""
import pymysql
from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)

from models import catalogo
from models import puesto as puesto_model


def _cargar_catalogo(slug=""):
    try:
        return catalogo.categorias(), catalogo.productos_activos(slug)
    except pymysql.MySQLError as error:
        # Si MySQL no responde, la página sigue con los datos de ejemplo.
        current_app.logger.error("Error de MySQL: %s", error)
        flash(
            "No pudimos conectar con la base de datos. "
            "Estás viendo datos de ejemplo.",
            "warning",
        )
        return catalogo.respaldo(slug)


def index():
    categorias, productos = _cargar_catalogo()
    return render_template("index.html", categorias=categorias, productos=productos)


def explorar():
    slug = request.args.get("categoria", "").strip()
    categorias, productos = _cargar_catalogo(slug)

    if slug and not any(c["slug"] == slug for c in categorias):
        abort(404)

    return render_template(
        "explorar.html", categorias=categorias, productos=productos, activa=slug
    )


def puestos():
    lista = []
    try:
        lista = puesto_model.listar()
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los puestos. Revisa la base de datos.", "danger")
    return render_template("puestos.html", puestos=lista)


def puesto_detalle(puesto_id):
    try:
        puesto = puesto_model.obtener(puesto_id)
        if puesto is None:
            abort(404)
        productos = puesto_model.productos_de(puesto_id)
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar ese puesto. Revisa la base de datos.", "danger")
        return redirect(url_for("puestos"))

    return render_template("puesto_detalle.html", puesto=puesto, productos=productos)


def mapa():
    datos = []
    try:
        for f in puesto_model.para_mapa():
            datos.append({
                "id": f["id"],
                "nombre": f["nombre"],
                "barrio": f["barrio"] or "",
                "lat": float(f["latitud"]),
                "lng": float(f["longitud"]),
                "abierto": bool(f["abierto"]),
                "url": url_for("puesto_detalle", puesto_id=f["id"]),
            })
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar el mapa. Revisa la base de datos.", "danger")
    return render_template("mapa.html", puestos=datos)


PROXIMAMENTE = {
    "vender": ("Vender con FRITOS TECH", "RF-01.5"),
    "recuperar-contrasena": ("Recuperar contraseña", "RF-01.3"),
}


def proximamente(pagina):
    if pagina not in PROXIMAMENTE:
        abort(404)
    titulo, rf = PROXIMAMENTE[pagina]
    return render_template("proximamente.html", titulo=titulo, rf=rf)
