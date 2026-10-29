"""Control de acceso por rol."""
from functools import wraps

from flask import flash, redirect, session, url_for


def vendedor_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como vendedor para ver tus productos.", "info")
            return redirect(url_for("acceso_rol", rol="vendedor"))
        if session.get("rol") != "vendedor":
            flash("Esta sección es solo para vendedores.", "warning")
            return redirect(url_for("explorar"))
        return vista(*args, **kwargs)
    return interior


def cliente_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como cliente para continuar con tu pedido.", "info")
            return redirect(url_for("acceso_rol", rol="cliente"))
        if session.get("rol") != "cliente":
            flash("Solo las cuentas de cliente pueden hacer pedidos.", "warning")
            return redirect(url_for("index"))
        return vista(*args, **kwargs)
    return interior


def admin_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como administrador.", "info")
            return redirect(url_for("acceso_rol", rol="administrador"))
        if session.get("rol") != "administrador":
            flash("Esta sección es solo para administradores.", "warning")
            return redirect(url_for("index"))
        return vista(*args, **kwargs)
    return interior
