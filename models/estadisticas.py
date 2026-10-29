"""Cifras del dashboard del administrador."""
from db import consultar

VACIAS = {
    "usuarios": 0, "vendedores": 0, "productos": 0,
    "productos_activos": 0, "categorias": 0,
    "pedidos": 0, "pendientes": 0, "ventas": 0,
}


def resumen():
    return consultar(
        "SELECT "
        " (SELECT COUNT(*) FROM usuario) AS usuarios,"
        " (SELECT COUNT(*) FROM usuario WHERE rol='vendedor' AND activo=1) AS vendedores,"
        " (SELECT COUNT(*) FROM producto) AS productos,"
        " (SELECT COUNT(*) FROM producto WHERE activo=1) AS productos_activos,"
        " (SELECT COUNT(*) FROM categoria) AS categorias,"
        " (SELECT COUNT(*) FROM pedido) AS pedidos,"
        " (SELECT COUNT(*) FROM pedido WHERE estado='pendiente') AS pendientes,"
        " (SELECT COALESCE(SUM(total),0) FROM pedido WHERE estado<>'cancelado') AS ventas",
        uno=True,
    )
