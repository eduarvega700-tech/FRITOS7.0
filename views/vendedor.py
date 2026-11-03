"""Vistas del panel del vendedor: resumen, productos y ventas."""
import os
import uuid

import pymysql
from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for)

from config import EXTENSIONES_IMAGEN
from decoradores import vendedor_requerido
from helpers import quitar_imagen
from imagenes import ruta_imagen
from models import categoria, producto, venta
from models.pedido import ESTADOS_PEDIDO


# ---------------------------------------------------------------- utilidades

def _falla_mysql(error, mensaje):
    """Registra el error y avisa. Con debug=True muestra además el detalle técnico."""
    current_app.logger.error("Error de MySQL: %s", error)
    if current_app.debug:
        mensaje += f" (detalle técnico: {error})"
    flash(mensaje, "danger")


def _categorias():
    try:
        return categoria.opciones()
    except pymysql.MySQLError as error:
        _falla_mysql(error, "No pudimos cargar las categorías.")
        return []


def _leer_formulario():
    """Lee y valida el formulario. Devuelve (datos, error); error=None si todo bien."""
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip(),
        "categoria_id": request.form.get("categoria_id", ""),
        "precio": request.form.get("precio", ""),
    }
    if (not datos["nombre"] or not datos["categoria_id"].isdigit()
            or not datos["precio"].isdigit()):
        return datos, "Completa el nombre, la categoría y el precio."
    if not 100 <= int(datos["precio"]) <= 1_000_000:
        return datos, "El precio debe estar entre $100 y $1.000.000."
    if len(datos["nombre"]) > 120 or len(datos["descripcion"]) > 255:
        return datos, "El nombre o la descripción son demasiado largos."
    return datos, None


def _guardar_imagen(archivo):
    """Guarda la foto (opcional). Devuelve (ruta o None, error o None)."""
    if not archivo or not archivo.filename:
        return None, None
    extension = archivo.filename.rsplit(".", 1)[-1].lower()
    if "." not in archivo.filename or extension not in EXTENSIONES_IMAGEN:
        return None, "La imagen debe ser JPG, PNG o WEBP."
    carpeta = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = f"{uuid.uuid4().hex}.{extension}"
    archivo.save(os.path.join(carpeta, nombre_archivo))
    return f"uploads/{nombre_archivo}", None


def _mensaje_mysql(error):
    codigo = error.args[0] if error.args else 0
    if codigo == 1062:
        return "Ya tienes un producto con ese nombre."
    if codigo == 1452:
        return "Esa categoría no existe."
    current_app.logger.error("Error de MySQL: %s", error)
    return "No pudimos guardar el producto."


# --------------------------------------------------------------------- panel

@vendedor_requerido
def panel_vendedor():
    vendedor_id = session["usuario_id"]
    resumen = dict(venta.VACIAS)
    recientes, mas_vendidos = [], []
    try:
        resumen = venta.resumen(vendedor_id)
        recientes = venta.lista(vendedor_id, limite=6)
        mas_vendidos = venta.mas_vendidos(vendedor_id)
    except pymysql.MySQLError as error:
        _falla_mysql(error, "No pudimos cargar todos los datos de tu panel.")
    return render_template(
        "vendedor_panel.html", resumen=resumen,
        recientes=recientes, mas_vendidos=mas_vendidos,
    )


# ----------------------------------------------------------------- productos

@vendedor_requerido
def mis_productos():
    productos = []
    try:
        productos = producto.de_vendedor(session["usuario_id"])
        for p in productos:
            p["foto"] = ruta_imagen(p["nombre"], p["imagen"])
    except pymysql.MySQLError as error:
        _falla_mysql(error, "No pudimos cargar tus productos. Revisa la base de datos.")
    return render_template("mis_productos.html", productos=productos)


@vendedor_requerido
def producto_nuevo():
    if request.method == "POST":
        datos, error = _leer_formulario()
        imagen = None
        if error is None:
            imagen, error = _guardar_imagen(request.files.get("imagen"))
        if error is None:
            try:
                producto.crear(
                    session["usuario_id"], int(datos["categoria_id"]),
                    datos["nombre"], datos["descripcion"] or None,
                    int(datos["precio"]), imagen,
                )
                flash(f"«{datos['nombre']}» ya está en tu catálogo.", "success")
                return redirect(url_for("mis_productos"))
            except pymysql.MySQLError as exc:
                quitar_imagen(imagen)
                error = _mensaje_mysql(exc)
        flash(error, "danger")
        return render_template(
            "producto_form.html", producto=datos,
            categorias=_categorias(), editando=False,
        )

    return render_template(
        "producto_form.html", producto={}, categorias=_categorias(),
        editando=False,
    )


@vendedor_requerido
def producto_editar(producto_id):
    actual = producto.obtener_de_vendedor(producto_id, session["usuario_id"])
    if actual is None:
        abort(404)
    actual["precio"] = int(actual["precio"])

    if request.method == "POST":
        datos, error = _leer_formulario()
        nueva = None
        if error is None:
            nueva, error = _guardar_imagen(request.files.get("imagen"))
        if error is None:
            try:
                producto.actualizar(
                    producto_id, session["usuario_id"],
                    int(datos["categoria_id"]), datos["nombre"],
                    datos["descripcion"] or None, int(datos["precio"]), nueva,
                )
                if nueva:
                    quitar_imagen(actual["imagen"])  # borra la foto anterior
                flash("Guardamos los cambios de tu producto.", "success")
                return redirect(url_for("mis_productos"))
            except pymysql.MySQLError as exc:
                quitar_imagen(nueva)
                error = _mensaje_mysql(exc)
        flash(error, "danger")
        formulario = dict(datos, id=actual["id"], imagen=actual["imagen"])
        return render_template(
            "producto_form.html", producto=formulario,
            categorias=_categorias(), editando=True,
        )

    return render_template(
        "producto_form.html", producto=actual,
        categorias=_categorias(), editando=True,
    )


@vendedor_requerido
def producto_estado(producto_id):
    # Oculta o vuelve a mostrar un producto (solo si es del vendedor).
    if producto.alternar_activo(producto_id, session["usuario_id"]) == 0:
        abort(404)
    flash("Listo, actualizamos la visibilidad del producto.", "success")
    return redirect(url_for("mis_productos"))


@vendedor_requerido
def producto_disponible(producto_id):
    # Marca un producto como agotado o disponible.
    if producto.alternar_disponible(producto_id, session["usuario_id"]) == 0:
        abort(404)
    flash("Listo, actualizamos la disponibilidad del producto.", "success")
    return redirect(url_for("mis_productos"))


@vendedor_requerido
def producto_eliminar(producto_id):
    fila = producto.imagen_de(producto_id, session["usuario_id"])
    if fila is None:
        abort(404)
    try:
        producto.eliminar(producto_id, session["usuario_id"])
    except pymysql.IntegrityError:
        flash(
            "No se puede eliminar porque ya tiene pedidos. "
            "Ocúltalo para que los clientes dejen de verlo.",
            "warning",
        )
        return redirect(url_for("mis_productos"))
    quitar_imagen(fila["imagen"])
    flash("Producto eliminado.", "success")
    return redirect(url_for("mis_productos"))


# -------------------------------------------------------------------- ventas

@vendedor_requerido
def mis_ventas():
    vendedor_id = session["usuario_id"]
    estado = request.args.get("estado", "").strip()
    if estado not in ESTADOS_PEDIDO:
        estado = ""
    resumen = dict(venta.VACIAS)
    pedidos, items = [], {}
    try:
        resumen = venta.resumen(vendedor_id)
        pedidos = venta.lista(vendedor_id, estado)
        items = venta.items(vendedor_id)
    except pymysql.MySQLError as error:
        _falla_mysql(error, "No pudimos cargar tus ventas.")
    return render_template(
        "mis_ventas.html", resumen=resumen, pedidos=pedidos, items=items,
        estados=ESTADOS_PEDIDO, estado_activo=estado,
    )
