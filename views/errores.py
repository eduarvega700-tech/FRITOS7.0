"""Páginas de error."""
from flask import flash, redirect, render_template, url_for


def registrar(app):
    @app.errorhandler(404)
    def no_encontrada(_):
        return render_template(
            "proximamente.html", titulo="No encontramos esa página", rf=None
        ), 404

    @app.errorhandler(400)
    def solicitud_invalida(_):
        # Normalmente: la página estuvo abierta mucho tiempo (token vencido).
        return render_template(
            "proximamente.html",
            titulo="Recarga la página e inténtalo de nuevo", rf=None,
        ), 400

    @app.errorhandler(413)
    def archivo_muy_grande(_):
        flash("La imagen es muy pesada (máximo 2 MB).", "danger")
        return redirect(url_for("mis_productos"))
