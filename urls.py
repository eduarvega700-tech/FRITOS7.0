"""Mapa de URLs -> vistas (el equivalente al urls.py de Django).

El nombre del endpoint es el nombre de la función de la vista, así que
todos los url_for('...') de tus templates siguen funcionando igual.
"""
from views import admin, auth, carrito, tienda, vendedor

GET = ["GET"]
POST = ["POST"]
GET_POST = ["GET", "POST"]

RUTAS = [
    # Tienda
    ("/", tienda.index, GET),
    ("/explorar", tienda.explorar, GET),
    ("/puestos", tienda.puestos, GET),
    ("/puestos/<int:puesto_id>", tienda.puesto_detalle, GET),
    ("/mapa", tienda.mapa, GET),

    # Autenticación
    ("/iniciar-sesion", auth.iniciar_sesion, GET),
    ("/acceso/<rol>", auth.acceso_rol, GET_POST),
    ("/salir", auth.salir, POST),
    ("/registro", auth.registro, GET),
    ("/registro/<rol>", auth.registro_rol, GET_POST),

    # Vendedor
    ("/mis-productos", vendedor.mis_productos, GET),
    ("/mis-productos/nuevo", vendedor.producto_nuevo, POST),
    ("/mis-productos/<int:producto_id>/estado", vendedor.producto_estado, POST),
    ("/mis-productos/<int:producto_id>/eliminar", vendedor.producto_eliminar, POST),

    # Carrito y pedidos
    ("/carrito", carrito.carrito, GET),
    ("/api/carrito", carrito.api_carrito, POST),
    ("/pedido", carrito.pedido_nuevo, POST),
    ("/mis-pedidos", carrito.mis_pedidos, GET),

    # Administrador
    ("/admin", admin.admin_dashboard, GET),
    ("/admin/usuarios", admin.admin_usuarios, GET),
    ("/admin/usuarios/<int:usuario_id>/estado", admin.admin_usuario_estado, POST),
    ("/admin/productos", admin.admin_productos, GET),
    ("/admin/productos/<int:producto_id>/estado", admin.admin_producto_estado, POST),
    ("/admin/productos/<int:producto_id>/eliminar", admin.admin_producto_eliminar, POST),
    ("/admin/categorias", admin.admin_categorias, GET_POST),
    ("/admin/categorias/<int:categoria_id>/eliminar", admin.admin_categoria_eliminar, POST),
    ("/admin/pedidos", admin.admin_pedidos, GET),
    ("/admin/pedidos/<int:pedido_id>/estado", admin.admin_pedido_estado, POST),

    # Páginas pendientes (siempre la última: atrapa /<pagina>)
    ("/<pagina>", tienda.proximamente, GET),
]


def registrar_urls(app):
    for ruta, vista, metodos in RUTAS:
        app.add_url_rule(ruta, view_func=vista, methods=metodos)
