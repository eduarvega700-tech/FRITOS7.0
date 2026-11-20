"""Modelo Producto (vendedor y administrador)."""
from db import consultar, ejecutar


def de_vendedor(vendedor_id):
    return consultar(
        "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
        "p.activo, p.disponible, p.cantidad_disponible, p.oferta_activa, "
        "p.descuento_porcentaje, p.creado_en, c.nombre AS categoria "
        "FROM producto p JOIN categoria c ON c.id = p.categoria_id "
        "WHERE p.vendedor_id = %s ORDER BY p.creado_en DESC, p.id DESC",
        (vendedor_id,),
    )


def crear(vendedor_id, categoria_id, nombre, descripcion, precio, imagen,
          cantidad_disponible, oferta_activa, descuento_porcentaje):
    return ejecutar(
        "INSERT INTO producto (vendedor_id, categoria_id, nombre, descripcion, precio, imagen, "
        "cantidad_disponible, disponible, oferta_activa, descuento_porcentaje) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (vendedor_id, categoria_id, nombre, descripcion, precio, imagen,
         cantidad_disponible, int(cantidad_disponible > 10), oferta_activa,
         descuento_porcentaje if oferta_activa else 0),
    )


def alternar_activo(producto_id, vendedor_id=None):
    sql = "UPDATE producto SET activo = 1 - activo WHERE id = %s"
    params = (producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id = %s"
        params += (vendedor_id,)
    return ejecutar(sql, params)


def obtener_de_vendedor(producto_id, vendedor_id):
    return consultar(
        "SELECT id,nombre,descripcion,precio,imagen,categoria_id,activo,disponible, "
        "cantidad_disponible,oferta_activa,descuento_porcentaje "
        "FROM producto WHERE id=%s AND vendedor_id=%s",
        (producto_id, vendedor_id), uno=True,
    )


def actualizar(producto_id, vendedor_id, categoria_id, nombre, descripcion,
               precio, cantidad_disponible, oferta_activa,
               descuento_porcentaje, imagen=None):
    sql = ("UPDATE producto SET categoria_id=%s,nombre=%s,descripcion=%s,precio=%s,"
           "cantidad_disponible=%s,disponible=%s,oferta_activa=%s,descuento_porcentaje=%s")
    params = [categoria_id,nombre,descripcion,precio,cantidad_disponible,
              int(cantidad_disponible > 0),oferta_activa,
              descuento_porcentaje if oferta_activa else 0]
    if imagen:
        sql += ", imagen=%s"
        params.append(imagen)
    sql += " WHERE id=%s AND vendedor_id=%s"
    params += [producto_id,vendedor_id]
    return ejecutar(sql, tuple(params))


def alternar_disponible(producto_id, vendedor_id):
    """Compatibilidad: solo permite reflejar agotado si no hay unidades."""
    return ejecutar(
        "UPDATE producto SET disponible = (cantidad_disponible > 0) "
        "WHERE id=%s AND vendedor_id=%s", (producto_id,vendedor_id)
    )


def imagen_de(producto_id, vendedor_id=None):
    sql="SELECT imagen FROM producto WHERE id=%s"; params=(producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id=%s"; params += (vendedor_id,)
    return consultar(sql,params,uno=True)


def eliminar(producto_id, vendedor_id=None):
    sql="DELETE FROM producto WHERE id=%s"; params=(producto_id,)
    if vendedor_id is not None:
        sql += " AND vendedor_id=%s"; params += (vendedor_id,)
    return ejecutar(sql,params)


def listar_todos():
    return consultar("SELECT p.id,p.nombre,p.precio,p.activo,p.imagen,p.creado_en, "
                     "u.nombre AS vendedor,c.nombre AS categoria FROM producto p "
                     "JOIN usuario u ON u.id=p.vendedor_id JOIN categoria c ON c.id=p.categoria_id "
                     "ORDER BY p.id DESC")


def recientes(limite=6):
    return consultar("SELECT p.nombre,u.nombre AS vendedor,c.nombre AS categoria,p.precio,p.activo "
                     "FROM producto p JOIN usuario u ON u.id=p.vendedor_id "
                     "JOIN categoria c ON c.id=p.categoria_id ORDER BY p.id DESC LIMIT %s",(limite,))
