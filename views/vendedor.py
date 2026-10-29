"""Vistas del panel del vendedor: mis productos."""
import os
import uuid

import pymysql
from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for)

from config import EXTENSIONES_IMAGEN
from decoradores import vendedor_requerido
from helpers import quitar_imagen
from models import categoria, producto


@vendedor_requerido
def mis_productos():
    productos, categorias = [], []
    try:
        productos = producto.de_vendedor(session["usuario_id"])
        categorias = categoria.opciones()
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar tus productos. Revisa la base de datos.", "danger")
    return render_template(
        "mis_productos.html", productos=productos, categorias=categorias
    )


@vendedor_requerido
def producto_nuevo():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    categoria_id = request.form.get("categoria_id", "")
    precio = request.form.get("precio", "")
    archivo = request.files.get("imagen")

    if not nombre or not categoria_id.isdigit() or not precio.isdigit():
        flash("Completa el nombre, la categoría y el precio.", "danger")
        return redirect(url_for("mis_productos"))

    precio = int(precio)
    if not 100 <= precio <= 1_000_000:
        flash("El precio debe estar entre $100 y $1.000.000.", "danger")
        return redirect(url_for("mis_productos"))

    if len(nombre) > 120 or len(descripcion) > 255:
        flash("El nombre o la descripción son demasiado largos.", "danger")
        return redirect(url_for("mis_productos"))

    # Foto (opcional).
    imagen = None
    if archivo and archivo.filename:
        extension = archivo.filename.rsplit(".", 1)[-1].lower()
        if "." not in archivo.filename or extension not in EXTENSIONES_IMAGEN:
            flash("La imagen debe ser JPG, PNG o WEBP.", "danger")
            return redirect(url_for("mis_productos"))

        carpeta = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(carpeta, exist_ok=True)
        nombre_archivo = f"{uuid.uuid4().hex}.{extension}"
        archivo.save(os.path.join(carpeta, nombre_archivo))
        imagen = f"uploads/{nombre_archivo}"

    try:
        producto.crear(
            session["usuario_id"], int(categoria_id), nombre,
            descripcion or None, precio, imagen,
        )
        flash(f"«{nombre}» ya está en tu catálogo.", "success")
    except pymysql.MySQLError as error:
        quitar_imagen(imagen)
        codigo = error.args[0] if error.args else 0
        if codigo == 1062:
            flash("Ya tienes un producto con ese nombre.", "danger")
        elif codigo == 1452:
            flash("Esa categoría no existe.", "danger")
        else:
            current_app.logger.error("Error de MySQL: %s", error)
            flash("No pudimos guardar el producto.", "danger")

    return redirect(url_for("mis_productos"))


@vendedor_requerido
def producto_estado(producto_id):
    # Oculta o vuelve a mostrar un producto (solo si es del vendedor).
    if producto.alternar_activo(producto_id, session["usuario_id"]) == 0:
        abort(404)
    flash("Listo, actualizamos la visibilidad del producto.", "success")
    return redirect(url_for("mis_productos"))


@vendedor_requerido
def producto_eliminar(producto_id):
    fila = producto.imagen_de(producto_id, session["usuario_id"])
    if fila is None:
        abort(404)
    producto.eliminar(producto_id, session["usuario_id"])
    quitar_imagen(fila["imagen"])
    flash("Producto eliminado.", "success")
    return redirect(url_for("mis_productos"))
