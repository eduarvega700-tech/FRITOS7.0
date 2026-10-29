"""Vistas de autenticación: roles, inicio de sesión, registro y salida."""
import pymysql
from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario
from models.roles import (ROLES_REGISTRO, buscar_rol, buscar_rol_acceso)


def destino_por_rol(rol):
    # El administrador y el vendedor entran a su panel; los demás a explorar.
    if rol == "administrador":
        return url_for("admin_dashboard")
    if rol == "vendedor":
        return url_for("mis_productos")
    return url_for("explorar")


def iniciar_sesion():
    return render_template("seleccionar_rol.html", roles=ROLES_REGISTRO)


def acceso_rol(rol):
    rol_actual = buscar_rol_acceso(rol)
    if rol_actual is None:
        abort(404)

    # Si ya inició sesión, lo llevamos directo a su página.
    if request.method == "GET" and "usuario_id" in session:
        return redirect(destino_por_rol(session.get("rol")))

    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("clave", "")

        if not correo or not clave:
            flash("Escribe tu correo y tu contraseña.", "danger")
            return redirect(url_for("acceso_rol", rol=rol))

        try:
            usr = usuario.buscar_para_login(correo, rol)
            if usr is None or not check_password_hash(usr["clave_hash"], clave):
                flash("Correo o contraseña incorrectos.", "danger")
                return redirect(url_for("acceso_rol", rol=rol))
            usuario.registrar_acceso(usr["id"], request.remote_addr)
        except pymysql.MySQLError as error:
            current_app.logger.error("Error de MySQL: %s", error)
            flash(
                "No pudimos conectar con la base de datos. "
                "Inténtalo de nuevo en unos minutos.",
                "danger",
            )
            return redirect(url_for("acceso_rol", rol=rol))

        # Sesión nueva (evita reutilizar sesiones anteriores).
        session.clear()
        session["usuario_id"] = usr["id"]
        session["nombre"] = usr["nombre"]
        session["rol"] = usr["rol"]
        return redirect(destino_por_rol(usr["rol"]))

    return render_template("auth.html", rol=rol_actual)


def salir():
    session.clear()
    flash("Cerraste sesión. ¡Vuelve pronto!", "info")
    return redirect(url_for("index"))


def registro():
    # Primero se debe seleccionar un rol.
    return redirect(url_for("iniciar_sesion"))


def registro_rol(rol):
    rol_actual = buscar_rol(rol)
    if rol_actual is None:
        abort(404)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        clave = request.form.get("clave", "")
        confirmar_clave = request.form.get("confirmar_clave", "")

        if not nombre or not correo or not clave or not confirmar_clave:
            flash("Completa todos los campos.", "danger")
        elif "@" not in correo or len(correo) > 150 or len(nombre) > 120:
            flash("Revisa tu nombre y tu correo electrónico.", "danger")
        elif clave != confirmar_clave:
            flash("Las contraseñas no coinciden.", "danger")
        elif len(clave) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
        else:
            try:
                usuario.crear(nombre, correo, generate_password_hash(clave), rol)
                flash("¡Cuenta creada! Ya puedes iniciar sesión.", "success")
                return redirect(url_for("acceso_rol", rol=rol))
            except pymysql.IntegrityError:
                flash("Ese correo ya está registrado.", "danger")
            except pymysql.MySQLError as error:
                current_app.logger.error("Error de MySQL: %s", error)
                flash(
                    "No pudimos conectar con la base de datos. "
                    "Inténtalo de nuevo en unos minutos.",
                    "danger",
                )
        return redirect(url_for("registro_rol", rol=rol))

    return render_template("registro.html", rol=rol_actual)
