"""Vistas del panel de administración."""
import pymysql
from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for)

from decoradores import admin_requerido
from helpers import crear_slug, quitar_imagen
from models import categoria, estadisticas, pedido, producto, usuario
from models.roles import ROLES_VALIDOS


@admin_requerido
def admin_dashboard():
    datos = dict(estadisticas.VACIAS)
    usuarios_recientes, productos_recientes, pedidos_recientes = [], [], []
    try:
        datos = estadisticas.resumen()
        usuarios_recientes = usuario.recientes()
        productos_recientes = producto.recientes()
        pedidos_recientes = pedido.recientes()
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar todos los datos del panel.", "danger")

    return render_template(
        "dashboard.html",
        estadisticas=datos,
        usuarios_recientes=usuarios_recientes,
        productos_recientes=productos_recientes,
        pedidos_recientes=pedidos_recientes,
    )


# --- Usuarios ---

@admin_requerido
def admin_usuarios():
    rol = request.args.get("rol", "").strip()
    if rol not in ROLES_VALIDOS:
        rol = ""
    usuarios = []
    try:
        usuarios = usuario.listar(rol)
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los usuarios.", "danger")
    return render_template("admin_usuarios.html", usuarios=usuarios, rol_activo=rol)


@admin_requerido
def admin_usuario_estado(usuario_id):
    if usuario_id == session["usuario_id"]:
        flash("No puedes desactivar tu propia cuenta.", "warning")
        return redirect(request.referrer or url_for("admin_usuarios"))
    if usuario.alternar_activo(usuario_id) == 0:
        abort(404)
    flash("Actualizamos el estado de la cuenta.", "success")
    return redirect(url_for("admin_usuarios", rol=request.form.get("rol", "")))


# --- Productos ---

@admin_requerido
def admin_productos():
    productos = []
    try:
        productos = producto.listar_todos()
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los productos.", "danger")
    return render_template("admin_productos.html", productos=productos)


@admin_requerido
def admin_producto_estado(producto_id):
    if producto.alternar_activo(producto_id) == 0:
        abort(404)
    flash("Actualizamos la visibilidad del producto.", "success")
    return redirect(url_for("admin_productos"))


@admin_requerido
def admin_producto_eliminar(producto_id):
    fila = producto.imagen_de(producto_id)
    if fila is None:
        abort(404)
    producto.eliminar(producto_id)
    quitar_imagen(fila["imagen"])
    flash("Producto eliminado.", "success")
    return redirect(url_for("admin_productos"))


# --- Categorías ---

@admin_requerido
def admin_categorias():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        slug = crear_slug(nombre)
        if not nombre or not slug or len(nombre) > 60:
            flash("Escribe un nombre válido (máximo 60 caracteres).", "danger")
        else:
            try:
                categoria.crear(nombre, slug)
                flash(f"Categoría «{nombre}» creada.", "success")
            except pymysql.IntegrityError:
                flash("Ya existe una categoría con ese nombre.", "danger")
            except pymysql.MySQLError as error:
                current_app.logger.error("Error de MySQL: %s", error)
                flash("No pudimos crear la categoría.", "danger")
        return redirect(url_for("admin_categorias"))

    categorias = []
    try:
        categorias = categoria.listar_con_conteo()
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar las categorías.", "danger")
    return render_template("admin_categorias.html", categorias=categorias)


@admin_requerido
def admin_categoria_eliminar(categoria_id):
    try:
        if categoria.eliminar(categoria_id) == 0:
            abort(404)
        flash("Categoría eliminada.", "success")
    except pymysql.IntegrityError:
        flash("No se puede eliminar: todavía tiene productos.", "danger")
    return redirect(url_for("admin_categorias"))


# --- Pedidos ---

@admin_requerido
def admin_pedidos():
    estado = request.args.get("estado", "").strip()
    if estado not in pedido.ESTADOS_PEDIDO:
        estado = ""
    pedidos, items = [], {}
    try:
        pedidos, items = pedido.todos(estado)
    except pymysql.MySQLError as error:
        current_app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los pedidos.", "danger")
    return render_template(
        "admin_pedidos.html", pedidos=pedidos, items=items,
        estados=pedido.ESTADOS_PEDIDO, estado_activo=estado,
    )


@admin_requerido
def admin_pedido_estado(pedido_id):
    estado = request.form.get("estado", "")
    if estado not in pedido.ESTADOS_PEDIDO:
        abort(400)
    if not pedido.cambiar_estado(pedido_id, estado):
        abort(404)
    flash(f"Pedido #{pedido_id} actualizado a «{estado}».", "success")
    return redirect(url_for("admin_pedidos", estado=request.form.get("filtro", "")))
