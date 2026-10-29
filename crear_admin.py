"""
Crea (o actualiza) la cuenta de administrador de FRITOS TECH.

Uso:   python crear_admin.py
Pide nombre, correo y contraseña por consola (la clave no se muestra).
"""
import getpass

from werkzeug.security import generate_password_hash

from app import app
from models import usuario


def main():
    nombre = input("Nombre del administrador: ").strip()
    correo = input("Correo: ").strip().lower()
    clave = getpass.getpass("Contraseña (mín. 8 caracteres): ")
    if not nombre or "@" not in correo or len(clave) < 8:
        print("Datos inválidos. No se creó nada.")
        return

    with app.app_context():
        usuario.crear_o_actualizar_admin(
            nombre, correo, generate_password_hash(clave)
        )
    print("Listo. Inicia sesión en /acceso/administrador")


if __name__ == "__main__":
    main()
