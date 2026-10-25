
def obtener_usuario_por_correo_y_rol(consultar, correo, rol):
    """Busca un usuario activo por correo y rol."""
    return consultar(
        "SELECT id, nombre, correo, clave_hash, rol "
        "FROM usuario "
        "WHERE correo = %s AND rol = %s AND activo = 1",
        (correo, rol),
        uno=True
    )


def actualizar_ultimo_acceso(ejecutar, usuario_id):
    """Actualiza la fecha del último acceso."""
    return ejecutar(
        "UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s",
        (usuario_id,)
    )


def registrar_historial_acceso(ejecutar, usuario_id, ip):
    """Guarda el historial de inicio de sesión."""
    return ejecutar(
        "INSERT INTO historial_acceso (usuario_id, ip) VALUES (%s, %s)",
        (usuario_id, ip)
    )
