"""Roles de la plataforma."""

# Estos roles pueden crear una cuenta desde la web.
ROLES_REGISTRO = [
    {"slug": "cliente", "nombre": "Cliente",
     "desc": "Compra tus fritos favoritos", "icono": "bi-cart3", "rf": "RF-01.1"},
    {"slug": "vendedor", "nombre": "Vendedor",
     "desc": "Publica tus productos", "icono": "bi-shop", "rf": "RF-01.5"},
    {"slug": "domiciliario", "nombre": "Domiciliario",
     "desc": "Haz entregas y genera ingresos", "icono": "bi-bicycle", "rf": "RF-01.6"},
]

# El administrador inicia sesión, pero NO se registra desde la web.
ROL_ADMIN = {
    "slug": "administrador", "nombre": "Administrador",
    "desc": "Gestiona la plataforma", "icono": "bi-shield-lock", "rf": "RF-01.7",
}

ROLES_VALIDOS = ("cliente", "vendedor", "domiciliario", "administrador")


def buscar_rol(slug):
    """Roles que pueden crear cuenta desde la web (registro)."""
    return next((r for r in ROLES_REGISTRO if r["slug"] == slug), None)


def buscar_rol_acceso(slug):
    """Roles que pueden iniciar sesión (incluye al administrador)."""
    if slug == ROL_ADMIN["slug"]:
        return ROL_ADMIN
    return buscar_rol(slug)
