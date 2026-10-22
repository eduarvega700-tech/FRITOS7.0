# 1. IMPORTACIONES

import hmac
import math
import os
import secrets
import uuid
from datetime import datetime
from functools import wraps

import pymysql
from pymysql.cursors import DictCursor
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# data.py ahora solo se usa como respaldo si MySQL no responde.
from data import CATEGORIAS, PRODUCTOS


# 2. CONFIGURACIÓN DE LA APLICACIÓN

app = Flask(__name__)

# Clave utilizada por Flask para proteger las sesiones y los mensajes.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "cambiar-en-produccion"
)

# Datos de conexión a MySQL.
# Se pueden cambiar con variables de entorno o editando los valores de abajo.
app.config["MYSQL"] = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DB", "fritos_tech"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
    "autocommit": True
}

# Carpeta donde se guardan las fotos que suben los vendedores.
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB
EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp"}


# 3. CONEXIÓN A MYSQL

def get_db():
    # Una conexión por petición; se cierra sola al terminar.
    if "db" not in g:
        g.db = pymysql.connect(**app.config["MYSQL"])
    return g.db


@app.teardown_appcontext
def cerrar_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def consultar(sql, params=(), uno=False):
    """SELECT: devuelve una fila (uno=True) o una lista de filas."""
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone() if uno else cur.fetchall()


def ejecutar(sql, params=()):
    """INSERT / UPDATE / DELETE: devuelve las filas afectadas."""
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


# 4. ROLES DISPONIBLES PARA EL REGISTRO

# Estos roles pueden crear una cuenta desde la página web.
# El administrador se crea directamente desde la base de datos.

ROLES_REGISTRO = [
    {
        "slug": "cliente",
        "nombre": "Cliente",
        "desc": "Compra tus fritos favoritos",
        "icono": "bi-cart3",
        "rf": "RF-01.1"
    },
    {
        "slug": "vendedor",
        "nombre": "Vendedor",
        "desc": "Publica tus productos",
        "icono": "bi-shop",
        "rf": "RF-01.5"
    },
    {
        "slug": "domiciliario",
        "nombre": "Domiciliario",
        "desc": "Haz entregas y genera ingresos",
        "icono": "bi-bicycle",
        "rf": "RF-01.6"
    }
]


def buscar_rol(slug):
    return next((r for r in ROLES_REGISTRO if r["slug"] == slug), None)


# 5. FILTRO PARA FORMATEAR PRECIOS EN PESOS COLOMBIANOS

@app.template_filter("cop")
def formato_cop(valor):
    """
    Convierte un número en un precio con formato colombiano.

    Ejemplo:
    2500 -> $2.500
    """
    return "$" + f"{valor:,.0f}".replace(",", ".")


# 6. SEGURIDAD: TOKEN CSRF PARA LOS FORMULARIOS

def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


@app.before_request
def verificar_csrf():
    # Todo formulario POST debe traer el token oculto csrf_token.
    if request.method == "POST":
        enviado = request.form.get("csrf_token", "")
        esperado = session.get("csrf", "")
        if not esperado or not hmac.compare_digest(
            enviado.encode(), esperado.encode()
        ):
            abort(400)


# 7. VARIABLES GLOBALES PARA LAS PLANTILLAS HTML

@app.context_processor
def variables_globales():
    return {
        "anio": datetime.now().year,   # {{ anio }}
        "csrf_token": token_csrf       # {{ csrf_token() }}
    }


# 8. SESIÓN: PROTEGER PÁGINAS Y ELEGIR A DÓNDE IR TRAS ENTRAR

def destino_por_rol(rol):
    # Cada rol entra a su panel; los demás a explorar.
    if rol == "vendedor":
        return url_for("mis_productos")
    if rol == "domiciliario":
        return url_for("dashboard_domiciliario")
    return url_for("explorar")


def domiciliario_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como domiciliario para ver tus entregas.", "info")
            return redirect(url_for("acceso_rol", rol="domiciliario"))
        if session.get("rol") != "domiciliario":
            flash("Esta sección es solo para domiciliarios.", "warning")
            return redirect(url_for("explorar"))
        return vista(*args, **kwargs)
    return interior


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


# 9. CATÁLOGO (CATEGORÍAS Y PRODUCTOS DESDE MYSQL)

def cargar_catalogo(slug=""):
    try:
        categorias = consultar(
            "SELECT nombre, slug, imagen FROM categoria ORDER BY id"
        )
        if slug:
            productos = consultar(
                "SELECT * FROM v_productos_activos "
                "WHERE categoria = %s ORDER BY id",
                (slug,)
            )
        else:
            productos = consultar(
                "SELECT * FROM v_productos_activos ORDER BY id"
            )
        return categorias, productos

    except pymysql.MySQLError as error:
        # Si MySQL no responde, la página sigue funcionando con data.py.
        app.logger.error("Error de MySQL: %s", error)
        flash(
            "No pudimos conectar con la base de datos. "
            "Estás viendo datos de ejemplo.",
            "warning"
        )
        productos = [
            p for p in PRODUCTOS
            if not slug or p["categoria"] == slug
        ]
        return CATEGORIAS, productos


# 10. PÁGINA PRINCIPAL

@app.route("/")
def index():
    categorias, productos = cargar_catalogo()
    return render_template(
        "index.html",
        categorias=categorias,
        productos=productos
    )


# 11. PÁGINA PARA EXPLORAR PRODUCTOS

@app.route("/explorar")
def explorar():
    slug = request.args.get("categoria", "").strip()

    categorias, productos = cargar_catalogo(slug)

    # Si la categoría no existe, mostrar error 404.
    if slug and not any(c["slug"] == slug for c in categorias):
        abort(404)

    return render_template(
        "explorar.html",
        categorias=categorias,
        productos=productos,
        activa=slug
    )


# 12. SELECCIONAR UN ROL

@app.route("/iniciar-sesion")
def iniciar_sesion():
    return render_template(
        "seleccionar_rol.html",
        roles=ROLES_REGISTRO
    )


# 13. INICIO DE SESIÓN

@app.route("/acceso/<rol>", methods=["GET", "POST"])
def acceso_rol(rol):

    rol_actual = buscar_rol(rol)
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
            usuario = consultar(
                "SELECT id, nombre, correo, clave_hash, rol "
                "FROM usuario "
                "WHERE correo = %s AND rol = %s AND activo = 1",
                (correo, rol),
                uno=True
            )

            if usuario is None or not check_password_hash(
                usuario["clave_hash"], clave
            ):
                flash("Correo o contraseña incorrectos.", "danger")
                return redirect(url_for("acceso_rol", rol=rol))

            ejecutar(
                "UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s",
                (usuario["id"],)
            )
            ejecutar(
                "INSERT INTO historial_acceso (usuario_id, ip) "
                "VALUES (%s, %s)",
                (usuario["id"], request.remote_addr)
            )

        except pymysql.MySQLError as error:
            app.logger.error("Error de MySQL: %s", error)
            flash(
                "No pudimos conectar con la base de datos. "
                "Inténtalo de nuevo en unos minutos.",
                "danger"
            )
            return redirect(url_for("acceso_rol", rol=rol))

        # Sesión nueva (evita reutilizar sesiones anteriores).
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["nombre"] = usuario["nombre"]
        session["rol"] = usuario["rol"]

        return redirect(destino_por_rol(usuario["rol"]))

    return render_template("auth.html", rol=rol_actual)


# 14. CERRAR SESIÓN

@app.route("/salir", methods=["POST"])
def salir():
    session.clear()
    flash("Cerraste sesión. ¡Vuelve pronto!", "info")
    return redirect(url_for("index"))


# 15. REGISTRO

@app.route("/registro")
def registro():
    # Primero se debe seleccionar un rol.
    return redirect(url_for("iniciar_sesion"))


@app.route("/registro/<rol>", methods=["GET", "POST"])
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
            flash(
                "La contraseña debe tener al menos 8 caracteres.",
                "danger"
            )

        else:
            try:
                ejecutar(
                    "INSERT INTO usuario (nombre, correo, clave_hash, rol) "
                    "VALUES (%s, %s, %s, %s)",
                    (nombre, correo, generate_password_hash(clave), rol)
                )
                flash(
                    "¡Cuenta creada! Ya puedes iniciar sesión.",
                    "success"
                )
                return redirect(url_for("acceso_rol", rol=rol))

            except pymysql.IntegrityError:
                flash("Ese correo ya está registrado.", "danger")

            except pymysql.MySQLError as error:
                app.logger.error("Error de MySQL: %s", error)
                flash(
                    "No pudimos conectar con la base de datos. "
                    "Inténtalo de nuevo en unos minutos.",
                    "danger"
                )

        return redirect(url_for("registro_rol", rol=rol))

    return render_template("registro.html", rol=rol_actual)


# 16. PANEL DEL VENDEDOR: MIS PRODUCTOS

def quitar_imagen(ruta):
    # Borra una foto subida (solo dentro de static/uploads).
    if ruta and ruta.startswith("uploads/"):
        try:
            os.remove(os.path.join(app.static_folder, ruta))
        except OSError:
            pass


@app.route("/mis-productos")
@vendedor_requerido
def mis_productos():
    productos, categorias = [], []
    try:
        productos = consultar(
            "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
            "       p.activo, p.creado_en, c.nombre AS categoria "
            "FROM producto p "
            "JOIN categoria c ON c.id = p.categoria_id "
            "WHERE p.vendedor_id = %s "
            "ORDER BY p.creado_en DESC, p.id DESC",
            (session["usuario_id"],)
        )
        categorias = consultar(
            "SELECT id, nombre FROM categoria ORDER BY id"
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar tus productos. Revisa la base de datos.", "danger")

    return render_template(
        "mis_productos.html",
        productos=productos,
        categorias=categorias
    )


@app.route("/mis-productos/nuevo", methods=["POST"])
@vendedor_requerido
def producto_nuevo():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    categoria_id = request.form.get("categoria_id", "")
    precio = request.form.get("precio", "")
    archivo = request.files.get("imagen")

    if not nombre or not categoria_id.isdigit() or not precio.isdigit():
        flash("Completa el nombre, la categoría y el precio.", "danger")
        return redirect(url_for("mis_productos"))

    precio = int(precio)
    if not 100 <= precio <= 1_000_000:
        flash("El precio debe estar entre $100 y $1.000.000.", "danger")
        return redirect(url_for("mis_productos"))

    if len(nombre) > 120 or len(descripcion) > 255:
        flash("El nombre o la descripción son demasiado largos.", "danger")
        return redirect(url_for("mis_productos"))

    # Foto (opcional).
    imagen = None
    if archivo and archivo.filename:
        extension = archivo.filename.rsplit(".", 1)[-1].lower()
        if "." not in archivo.filename or extension not in EXTENSIONES_IMAGEN:
            flash("La imagen debe ser JPG, PNG o WEBP.", "danger")
            return redirect(url_for("mis_productos"))

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        nombre_archivo = f"{uuid.uuid4().hex}.{extension}"
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
        imagen = f"uploads/{nombre_archivo}"

    try:
        ejecutar(
            "INSERT INTO producto "
            "(vendedor_id, categoria_id, nombre, descripcion, precio, imagen) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (
                session["usuario_id"],
                int(categoria_id),
                nombre,
                descripcion or None,
                precio,
                imagen
            )
        )
        flash(f"«{nombre}» ya está en tu catálogo.", "success")

    except pymysql.MySQLError as error:
        quitar_imagen(imagen)
        codigo = error.args[0] if error.args else 0
        if codigo == 1062:
            flash("Ya tienes un producto con ese nombre.", "danger")
        elif codigo == 1452:
            flash("Esa categoría no existe.", "danger")
        else:
            app.logger.error("Error de MySQL: %s", error)
            flash("No pudimos guardar el producto.", "danger")

    return redirect(url_for("mis_productos"))


@app.route("/mis-productos/<int:producto_id>/estado", methods=["POST"])
@vendedor_requerido
def producto_estado(producto_id):
    # Oculta o vuelve a mostrar un producto (solo si es del vendedor).
    filas = ejecutar(
        "UPDATE producto SET activo = 1 - activo "
        "WHERE id = %s AND vendedor_id = %s",
        (producto_id, session["usuario_id"])
    )
    if filas == 0:
        abort(404)
    flash("Listo, actualizamos la visibilidad del producto.", "success")
    return redirect(url_for("mis_productos"))


@app.route("/mis-productos/<int:producto_id>/eliminar", methods=["POST"])
@vendedor_requerido
def producto_eliminar(producto_id):
    producto = consultar(
        "SELECT imagen FROM producto WHERE id = %s AND vendedor_id = %s",
        (producto_id, session["usuario_id"]),
        uno=True
    )
    if producto is None:
        abort(404)

    ejecutar(
        "DELETE FROM producto WHERE id = %s AND vendedor_id = %s",
        (producto_id, session["usuario_id"])
    )
    quitar_imagen(producto["imagen"])
    flash("Producto eliminado.", "success")
    return redirect(url_for("mis_productos"))


# 16 BIS. PANEL DEL DOMICILIARIO

# Máximo de pedidos que un repartidor puede llevar al mismo tiempo.
MAX_ENTREGAS_ACTIVAS = 3

# Consulta base: pedido + cliente + local del vendedor (punto de recogida).
# Cada consulta le agrega su propio WHERE / ORDER BY.
SQL_PEDIDO = (
    "SELECT p.id, p.estado, p.total, p.costo_domicilio, p.metodo_pago, "
    "       p.notas, p.direccion_entrega, p.barrio, p.referencia, "
    "       p.telefono_contacto, p.latitud AS destino_lat, "
    "       p.longitud AS destino_lng, p.creado_en, p.entregado_en, "
    "       p.vendedor_id, cli.nombre AS cliente, "
    "       COALESCE(l.nombre_local, ven.nombre) AS local, "
    "       l.direccion AS local_direccion, l.barrio AS local_barrio, "
    "       l.telefono AS local_telefono, "
    "       l.latitud AS local_lat, l.longitud AS local_lng "
    "FROM pedido p "
    "JOIN usuario cli ON cli.id = p.cliente_id "
    "JOIN usuario ven ON ven.id = p.vendedor_id "
    "LEFT JOIN local_vendedor l ON l.vendedor_id = p.vendedor_id "
)


def distancia_km(lat1, lng1, lat2, lng2):
    # Distancia en línea recta entre dos puntos (fórmula de Haversine).
    if None in (lat1, lng1, lat2, lng2):
        return None
    radio = 6371
    f1, f2 = math.radians(lat1), math.radians(lat2)
    df = f2 - f1
    dl = math.radians(lng2 - lng1)
    a = (
        math.sin(df / 2) ** 2
        + math.cos(f1) * math.cos(f2) * math.sin(dl / 2) ** 2
    )
    return round(radio * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)


def completar_pedidos(pedidos):
    # Agrega a cada pedido sus fritos (lineas), cantidad y distancia.
    if not pedidos:
        return pedidos

    ids = [p["id"] for p in pedidos]
    marcas = ", ".join(["%s"] * len(ids))
    filas = consultar(
        "SELECT pedido_id, nombre, cantidad FROM pedido_detalle "
        "WHERE pedido_id IN (" + marcas + ") ORDER BY id",
        tuple(ids)
    )
    por_pedido = {}
    for fila in filas:
        por_pedido.setdefault(fila["pedido_id"], []).append(fila)

    for p in pedidos:
        p["lineas"] = por_pedido.get(p["id"], [])
        p["articulos"] = sum(l["cantidad"] for l in p["lineas"])
        p["distancia_km"] = distancia_km(
            p["local_lat"], p["local_lng"],
            p["destino_lat"], p["destino_lng"]
        )
    return pedidos


def resumen_entregas(uid, solo_hoy):
    filtro = " AND DATE(entregado_en) = CURDATE()" if solo_hoy else ""
    fila = consultar(
        "SELECT COUNT(*) AS entregas, "
        "       COALESCE(SUM(costo_domicilio), 0) AS ganancias "
        "FROM pedido WHERE repartidor_id = %s AND estado = 'entregado'"
        + filtro,
        (uid,),
        uno=True
    )
    return {"entregas": int(fila["entregas"]), "ganancias": int(fila["ganancias"])}


@app.route("/domiciliario")
@domiciliario_requerido
def dashboard_domiciliario():
    uid = session["usuario_id"]

    perfil = {
        "disponible": 0, "vehiculo": "moto", "placa": None,
        "telefono": None, "latitud": None, "longitud": None
    }
    activos, disponibles, historial = [], [], []
    hoy = {"entregas": 0, "ganancias": 0}
    total = {"entregas": 0, "ganancias": 0}

    try:
        # Si es su primera vez, se crea su perfil de repartidor.
        ejecutar(
            "INSERT IGNORE INTO repartidor (usuario_id) VALUES (%s)",
            (uid,)
        )
        perfil = consultar(
            "SELECT disponible, vehiculo, placa, telefono, latitud, longitud "
            "FROM repartidor WHERE usuario_id = %s",
            (uid,),
            uno=True
        ) or perfil

        # Entregas que ya aceptó (por recoger o en camino).
        activos = completar_pedidos(consultar(
            SQL_PEDIDO +
            "WHERE p.repartidor_id = %s "
            "  AND p.estado IN ('asignado', 'en_camino') "
            "ORDER BY FIELD(p.estado, 'en_camino', 'asignado'), p.creado_en",
            (uid,)
        ))

        # Pedidos sin repartidor que alguien puede tomar.
        disponibles = completar_pedidos(consultar(
            SQL_PEDIDO +
            "WHERE p.repartidor_id IS NULL "
            "  AND p.estado IN ('listo', 'preparando') "
            "ORDER BY FIELD(p.estado, 'listo', 'preparando'), p.creado_en "
            "LIMIT 20"
        ))

        historial = completar_pedidos(consultar(
            SQL_PEDIDO +
            "WHERE p.repartidor_id = %s AND p.estado = 'entregado' "
            "ORDER BY p.entregado_en DESC LIMIT 8",
            (uid,)
        ))

        hoy = resumen_entregas(uid, solo_hoy=True)
        total = resumen_entregas(uid, solo_hoy=False)

    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        codigo = error.args[0] if error.args else 0
        if codigo == 1146:
            flash(
                "Faltan las tablas del domiciliario. "
                "Ejecuta el archivo repartidor.sql en MySQL.",
                "danger"
            )
        else:
            flash("No pudimos cargar tus entregas. Revisa la base de datos.", "danger")

    # Datos para el mapa (se envían como JSON a la plantilla).
    def punto(lat, lng):
        return None if lat is None or lng is None else [lat, lng]

    mapa = []
    for tipo, lista in (("activo", activos), ("disponible", disponibles)):
        for p in lista:
            mapa.append({
                "id": p["id"],
                "tipo": tipo,
                "estado": p["estado"],
                "local": p["local"],
                "local_direccion": p["local_direccion"],
                "local_pos": punto(p["local_lat"], p["local_lng"]),
                "cliente": p["cliente"],
                "destino": p["direccion_entrega"],
                "barrio": p["barrio"],
                "destino_pos": punto(p["destino_lat"], p["destino_lng"])
            })

    # Locales donde hay que recoger (agrupados por vendedor).
    locales = {}
    for tipo, lista in (("activos", activos), ("disponibles", disponibles)):
        for p in lista:
            local = locales.setdefault(p["vendedor_id"], {
                "nombre": p["local"],
                "direccion": p["local_direccion"],
                "barrio": p["local_barrio"],
                "telefono": p["local_telefono"],
                "lat": p["local_lat"],
                "lng": p["local_lng"],
                "activos": 0,
                "disponibles": 0
            })
            local[tipo] += 1
    locales = sorted(
        locales.values(),
        key=lambda x: (-x["activos"], -x["disponibles"], x["nombre"])
    )

    return render_template(
        "dashboard_repartidor.html",
        perfil=perfil,
        activos=activos,
        disponibles=disponibles,
        historial=historial,
        locales=locales,
        hoy=hoy,
        total=total,
        mapa=mapa,
        max_activas=MAX_ENTREGAS_ACTIVAS
    )


@app.route("/domiciliario/disponibilidad", methods=["POST"])
@domiciliario_requerido
def repartidor_disponibilidad():
    uid = session["usuario_id"]
    try:
        ejecutar(
            "INSERT IGNORE INTO repartidor (usuario_id) VALUES (%s)", (uid,)
        )
        ejecutar(
            "UPDATE repartidor SET disponible = 1 - disponible "
            "WHERE usuario_id = %s",
            (uid,)
        )
        perfil = consultar(
            "SELECT disponible FROM repartidor WHERE usuario_id = %s",
            (uid,),
            uno=True
        )
        if perfil and perfil["disponible"]:
            flash("Estás disponible: ya puedes tomar pedidos.", "success")
        else:
            flash("Quedaste no disponible. No tomarás pedidos nuevos.", "info")
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cambiar tu disponibilidad.", "danger")
    return redirect(url_for("dashboard_domiciliario"))


@app.route("/domiciliario/pedidos/<int:pedido_id>/aceptar", methods=["POST"])
@domiciliario_requerido
def pedido_aceptar(pedido_id):
    uid = session["usuario_id"]
    try:
        perfil = consultar(
            "SELECT disponible FROM repartidor WHERE usuario_id = %s",
            (uid,),
            uno=True
        )
        en_curso = consultar(
            "SELECT COUNT(*) AS n FROM pedido "
            "WHERE repartidor_id = %s AND estado IN ('asignado', 'en_camino')",
            (uid,),
            uno=True
        )["n"]

        if not perfil or not perfil["disponible"]:
            flash("Activa tu disponibilidad para tomar pedidos.", "warning")
        elif en_curso >= MAX_ENTREGAS_ACTIVAS:
            flash(
                f"Ya llevas {MAX_ENTREGAS_ACTIVAS} entregas a la vez. "
                "Termina una para tomar otra.",
                "warning"
            )
        else:
            # La condición repartidor_id IS NULL evita que dos repartidores
            # tomen el mismo pedido al mismo tiempo.
            filas = ejecutar(
                "UPDATE pedido "
                "SET repartidor_id = %s, estado = 'asignado', "
                "    aceptado_en = NOW() "
                "WHERE id = %s AND repartidor_id IS NULL "
                "  AND estado = 'listo'",
                (uid, pedido_id)
            )
            if filas:
                flash(f"Pedido #{pedido_id} asignado. ¡Ve a recogerlo!", "success")
            else:
                flash(
                    "Ese pedido ya no está disponible "
                    "(otro repartidor lo tomó o sigue en preparación).",
                    "warning"
                )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos asignarte el pedido.", "danger")
    return redirect(url_for("dashboard_domiciliario"))


def mover_pedido(pedido_id, desde, hasta, columna_hora, mensaje):
    # Cambia el estado de un pedido que pertenece al repartidor actual.
    # "columna_hora" siempre es un texto fijo escrito aquí, nunca del usuario.
    try:
        filas = ejecutar(
            "UPDATE pedido SET estado = %s, " + columna_hora + " = NOW() "
            "WHERE id = %s AND repartidor_id = %s AND estado = %s",
            (hasta, pedido_id, session["usuario_id"], desde)
        )
        if filas:
            flash(mensaje, "success")
        else:
            flash("No pudimos actualizar ese pedido.", "warning")
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos actualizar el pedido.", "danger")
    return redirect(url_for("dashboard_domiciliario"))


@app.route("/domiciliario/pedidos/<int:pedido_id>/recoger", methods=["POST"])
@domiciliario_requerido
def pedido_recoger(pedido_id):
    return mover_pedido(
        pedido_id, "asignado", "en_camino", "recogido_en",
        f"Pedido #{pedido_id} recogido. ¡Buen viaje!"
    )


@app.route("/domiciliario/pedidos/<int:pedido_id>/entregar", methods=["POST"])
@domiciliario_requerido
def pedido_entregar(pedido_id):
    return mover_pedido(
        pedido_id, "en_camino", "entregado", "entregado_en",
        f"Pedido #{pedido_id} entregado. ¡Buen trabajo!"
    )


@app.route("/domiciliario/pedidos/<int:pedido_id>/soltar", methods=["POST"])
@domiciliario_requerido
def pedido_soltar(pedido_id):
    # Devuelve a la lista un pedido que aún no recogió.
    try:
        filas = ejecutar(
            "UPDATE pedido SET repartidor_id = NULL, estado = 'listo', "
            "       aceptado_en = NULL "
            "WHERE id = %s AND repartidor_id = %s AND estado = 'asignado'",
            (pedido_id, session["usuario_id"])
        )
        if filas:
            flash(f"Soltaste el pedido #{pedido_id}.", "info")
        else:
            flash("Solo puedes soltar pedidos que aún no has recogido.", "warning")
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos soltar el pedido.", "danger")
    return redirect(url_for("dashboard_domiciliario"))


@app.route("/domiciliario/ubicacion", methods=["POST"])
@domiciliario_requerido
def repartidor_ubicacion():
    # El navegador envía aquí la posición GPS del repartidor.
    try:
        lat = float(request.form.get("lat", ""))
        lng = float(request.form.get("lng", ""))
    except ValueError:
        abort(400)

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        abort(400)

    try:
        ejecutar(
            "UPDATE repartidor SET latitud = %s, longitud = %s, "
            "       ubicacion_actualizada = NOW() "
            "WHERE usuario_id = %s",
            (lat, lng, session["usuario_id"])
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        return "", 500
    return "", 204


# 17. PÁGINAS QUE TODAVÍA ESTÁN PENDIENTES

PROXIMAMENTE = {
    "vender": (
        "Vender con FRITOS TECH",
        "RF-01.5"
    ),
    "recuperar-contrasena": (
        "Recuperar contraseña",
        "RF-01.3"
    )
}


@app.route("/<pagina>")
def proximamente(pagina):

    if pagina not in PROXIMAMENTE:
        abort(404)

    titulo, rf = PROXIMAMENTE[pagina]

    return render_template(
        "proximamente.html",
        titulo=titulo,
        rf=rf
    )


# 18. MANEJO DE ERRORES

@app.errorhandler(404)
def no_encontrada(_):
    return render_template(
        "proximamente.html",
        titulo="No encontramos esa página",
        rf=None
    ), 404


@app.errorhandler(400)
def solicitud_invalida(_):
    # Normalmente: la página estuvo abierta mucho tiempo (token vencido).
    return render_template(
        "proximamente.html",
        titulo="Recarga la página e inténtalo de nuevo",
        rf=None
    ), 400


@app.errorhandler(413)
def archivo_muy_grande(_):
    flash("La imagen es muy pesada (máximo 2 MB).", "danger")
    return redirect(url_for("mis_productos"))


# 19. EJECUTAR LA APLICACIÓN

if __name__ == "__main__":
    app.run(debug=True)
