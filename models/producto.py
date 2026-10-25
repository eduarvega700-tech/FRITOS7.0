
import pymysql


def obtener_categorias(consultar):
    """Obtiene las categorías registradas en MySQL."""
    return consultar(
        "SELECT nombre, slug, imagen FROM categoria ORDER BY id"
    )


def obtener_productos(consultar, categoria=""):
    """Obtiene los productos activos, opcionalmente por categoría."""
    if categoria:
        return consultar(
            "SELECT * FROM v_productos_activos "
            "WHERE categoria = %s ORDER BY id",
            (categoria,)
        )

    return consultar(
        "SELECT * FROM v_productos_activos ORDER BY id"
    )


def obtener_productos_vendedor(consultar, vendedor_id):
    """Obtiene los productos de un vendedor."""
    return consultar(
        "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
        "p.activo, p.creado_en, c.nombre AS categoria "
        "FROM producto p "
        "JOIN categoria c ON c.id = p.categoria_id "
        "WHERE p.vendedor_id = %s "
        "ORDER BY p.creado_en DESC, p.id DESC",
        (vendedor_id,)
    )


def obtener_categorias_vendedor(consultar):
    """Obtiene las categorías disponibles para los vendedores."""
    return consultar(
        "SELECT id, nombre FROM categoria ORDER BY id"
    )
