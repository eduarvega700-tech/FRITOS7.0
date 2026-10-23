# 1. IMPORTACIONES

import hmac
import json
import os
import re
import secrets
import unicodedata
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
    jsonify,
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


# El administrador puede iniciar sesión, pero NO registrarse desde la web.
ROL_ADMIN = {
    "slug": "administrador",
    "nombre": "Administrador",
    "desc": "Gestiona la plataforma",
    "icono": "bi-shield-lock",
    "rf": "RF-01.7"
}


def buscar_rol(slug):
    """Roles que pueden crear cuenta desde la web (registro)."""
    return next((r for r in ROLES_REGISTRO if r["slug"] == slug), None)


def buscar_rol_acceso(slug):
    """Roles que pueden iniciar sesión (incluye al administrador)."""
    if slug == ROL_ADMIN["slug"]:
        return ROL_ADMIN
    return buscar_rol(slug)


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
        enviado = (
            request.form.get("csrf_token", "")
            or request.headers.get("X-CSRF-Token", "")
        )
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
    # El administrador y el vendedor entran a su panel; los demás a explorar.
    if rol == "administrador":
        return url_for("admin_dashboard")
    if rol == "vendedor":
        return url_for("mis_productos")
    return url_for("explorar")


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


def admin_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como administrador.", "info")
            return redirect(url_for("acceso_rol", rol="administrador"))
        if session.get("rol") != "administrador":
            flash("Esta sección es solo para administradores.", "warning")
            return redirect(url_for("index"))
        return vista(*args, **kwargs)
    return interior


def cliente_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como cliente para continuar con tu pedido.", "info")
            return redirect(url_for("acceso_rol", rol="cliente"))
        if session.get("rol") != "cliente":
            flash("Solo las cuentas de cliente pueden hacer pedidos.", "warning")
            return redirect(url_for("index"))
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


# 17. CARRITO Y PEDIDOS

# Fotos de los productos de ejemplo (las mismas que usan index.html y explorar.html).
IMAGENES_PRODUCTOS = {
    "Empanadas de carne": "empanadas_de_carne.jpg",
    "Empanada de pollo": "empanadas_pollo.jpg",
    "Arepa de huevo": "arepa_huevo.jpg",
    "Arepa de huevo especial": "arepa_huevo_especial.jpg",
    "Carimañolas de yuca": "carimañolas_de_yuca.jpg",
    "Patacones con hogao": "patacones_con_hogao.jpg",
    "Patacón con queso": "patacon_con_queso.jpg",
    "Buñuelos": "bunuelos.jpg",
    "Empanadas de queso": "empanadas_de_queso.jpg",
    "Carimañolas de queso": "carimanolas_de_queso.jpg",
    "Arepa de huevo con carne": "arepa_huevo_carne.jpg",
    "Arepa de huevo con queso": "arepa_huevo_queso.jpg",
    "Papa rellena": "papa_rellena.jpg",
    "Deditos de queso": "deditos_queso.jpg",
    "Marranitas": "marranitas.jpg",
    "Aborrajados": "aborrajados.jpg",
    "Quibbes": "quibbes.jpg",
    "Pastel de pollo": "pastel_pollo.jpg",
    "Yuca frita": "yuca_frita.jpg",
    "Tajadas de plátano maduro": "tajadas_platano_maduro.jpg",
    "Papas criollas fritas": "papas_criollas_fritas.jpg",
    "Chicharrón": "chicharron.jpg",
    "Empanadas de pipián": "empanadas_pipian.jpg",
    "Empanadas de camarón": "empanadas_camaron.jpg",
    "Buñuelos de frijol": "bunuelos_frijol.jpg",
    "Pasteles de yuca": "pasteles_yuca.jpg",
    "Arepa frita": "arepa_frita.jpg",
    "Patacón pisao": "patacon_pisao.jpg",
    "Hojaldras": "hojaldras.jpg",
    "Empanadas vallecaucanas": "empanadas_vallecaucanas.jpg",
    "Empanadas de cambray": "empanadas_cambray.jpg",
    "Empanadas de yuca": "empanadas_yuca.jpg",
    "Bolitas de yuca con queso": "bolitas_yuca_queso.jpg",
    "Arepa de choclo frita": "arepa_choclo_frita.jpg",
    "Cazón frito": "cazon_frito.jpg",
    "Plátano relleno frito": "platano_relleno_frito.jpg",
    "Tostadas de plátano verde": "tostadas_platano_verde.jpg",
    "Papa rellena con arroz y huevo": "papa_rellena_arroz_huevo.jpg",
}

MAX_UNIDADES = 50          # máximo por producto en un pedido
ESTADOS_PEDIDO = ["pendiente", "preparando", "listo", "entregado", "cancelado"]
TIPOS_ENTREGA = ["recoger", "domicilio"]


def ruta_imagen(nombre, imagen):
    """Ruta relativa a /static de la foto de un producto."""
    if imagen and imagen.startswith("uploads/"):
        return imagen
    return "img/" + IMAGENES_PRODUCTOS.get(nombre, "logito.png")


def leer_items(texto):
    """Convierte {"id": cantidad} (JSON) en {id:int -> cantidad:int} validado."""
    try:
        bruto = json.loads(texto or "{}")
    except (TypeError, ValueError):
        return {}
    if not isinstance(bruto, dict):
        return {}
    items = {}
    for clave, cantidad in bruto.items():
        try:
            producto_id, cantidad = int(clave), int(cantidad)
        except (TypeError, ValueError):
            continue
        if producto_id > 0 and cantidad > 0:
            items[producto_id] = min(cantidad, MAX_UNIDADES)
    return items


def productos_por_ids(ids):
    """Productos visibles (de MySQL) para los ids dados."""
    if not ids:
        return []
    marcas = ",".join(["%s"] * len(ids))
    return consultar(
        "SELECT id, nombre, vendedor, precio, img "
        "FROM v_productos_activos WHERE id IN (" + marcas + ")",
        tuple(ids)
    )


@app.route("/carrito")
def carrito():
    # El contenido del carrito vive en el navegador; main.js lo dibuja
    # pidiendo los datos reales (precios, fotos) a /api/carrito.
    if session.get("rol") == "administrador":
        return redirect(url_for("admin_dashboard"))
    return render_template("carrito.html", max_unidades=MAX_UNIDADES)


@app.route("/api/carrito", methods=["POST"])
def api_carrito():
    # Devuelve los datos actuales de los productos del carrito.
    datos = request.get_json(silent=True) or {}
    items = leer_items(json.dumps(datos.get("items", {})))
    try:
        filas = productos_por_ids(list(items))
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        return jsonify({"error": "db"}), 503

    productos = [{
        "id": f["id"],
        "nombre": f["nombre"],
        "vendedor": f["vendedor"],
        "precio": int(f["precio"]),
        "cantidad": items[f["id"]],
        "img": url_for("static", filename=ruta_imagen(f["nombre"], f["img"]))
    } for f in filas]
    return jsonify({"productos": productos})


@app.route("/pedido", methods=["POST"])
@cliente_requerido
def pedido_nuevo():
    items = leer_items(request.form.get("items", ""))
    tipo = request.form.get("tipo_entrega", "")
    direccion = request.form.get("direccion", "").strip()
    notas = request.form.get("notas", "").strip()

    if not items:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("carrito"))
    if tipo not in TIPOS_ENTREGA:
        flash("Elige si quieres recoger o recibir a domicilio.", "danger")
        return redirect(url_for("carrito"))
    if tipo == "domicilio" and len(direccion) < 6:
        flash("Escribe la dirección de entrega.", "danger")
        return redirect(url_for("carrito"))
    if len(direccion) > 200 or len(notas) > 255:
        flash("La dirección o las notas son demasiado largas.", "danger")
        return redirect(url_for("carrito"))

    try:
        db = get_db()
        filas = productos_por_ids(list(items))
        # Los precios SIEMPRE se toman de la base de datos, nunca del navegador.
        if len(filas) != len(items):
            flash(
                "Algún producto ya no está disponible. "
                "Revisa tu carrito.", "warning"
            )
            return redirect(url_for("carrito"))

        total = sum(int(f["precio"]) * items[f["id"]] for f in filas)

        db.begin()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO pedido "
                "(cliente_id, tipo_entrega, direccion, notas, total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    session["usuario_id"], tipo,
                    direccion if tipo == "domicilio" else None,
                    notas or None, total
                )
            )
            pedido_id = cur.lastrowid
            for f in filas:
                cur.execute(
                    "INSERT INTO pedido_item "
                    "(pedido_id, producto_id, nombre, precio_unitario, cantidad) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (pedido_id, f["id"], f["nombre"],
                     int(f["precio"]), items[f["id"]])
                )
        db.commit()

    except pymysql.MySQLError as error:
        if "db" in g:
            try:
                g.db.rollback()
            except pymysql.MySQLError:
                pass
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos registrar tu pedido. Inténtalo de nuevo.", "danger")
        return redirect(url_for("carrito"))

    flash(f"¡Pedido #{pedido_id} recibido! Te avisaremos cuando avance.", "success")
    # vaciar=1 le dice a main.js que limpie el carrito del navegador.
    return redirect(url_for("mis_pedidos", vaciar=1))


@app.route("/mis-pedidos")
@cliente_requerido
def mis_pedidos():
    pedidos, items = [], {}
    try:
        pedidos = consultar(
            "SELECT id, tipo_entrega, direccion, notas, total, estado, creado_en "
            "FROM pedido WHERE cliente_id = %s ORDER BY id DESC",
            (session["usuario_id"],)
        )
        for it in consultar(
            "SELECT i.pedido_id, i.nombre, i.precio_unitario, i.cantidad "
            "FROM pedido_item i JOIN pedido p ON p.id = i.pedido_id "
            "WHERE p.cliente_id = %s ORDER BY i.id",
            (session["usuario_id"],)
        ):
            items.setdefault(it["pedido_id"], []).append(it)
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar tus pedidos.", "danger")
    return render_template(
        "mis_pedidos.html", pedidos=pedidos, items=items,
        vaciar=request.args.get("vaciar") == "1"
    )


# 18. PANEL DEL ADMINISTRADOR

@app.route("/admin")
@admin_requerido
def admin_dashboard():
    estadisticas = {
        "usuarios": 0, "vendedores": 0, "productos": 0,
        "productos_activos": 0, "categorias": 0,
        "pedidos": 0, "pendientes": 0, "ventas": 0
    }
    usuarios_recientes, productos_recientes, pedidos_recientes = [], [], []
    try:
        estadisticas = consultar(
            "SELECT "
            " (SELECT COUNT(*) FROM usuario) AS usuarios,"
            " (SELECT COUNT(*) FROM usuario WHERE rol='vendedor' AND activo=1) AS vendedores,"
            " (SELECT COUNT(*) FROM producto) AS productos,"
            " (SELECT COUNT(*) FROM producto WHERE activo=1) AS productos_activos,"
            " (SELECT COUNT(*) FROM categoria) AS categorias,"
            " (SELECT COUNT(*) FROM pedido) AS pedidos,"
            " (SELECT COUNT(*) FROM pedido WHERE estado='pendiente') AS pendientes,"
            " (SELECT COALESCE(SUM(total),0) FROM pedido WHERE estado<>'cancelado') AS ventas",
            uno=True
        )
        usuarios_recientes = consultar(
            "SELECT nombre, correo, rol, activo, creado_en "
            "FROM usuario ORDER BY id DESC LIMIT 6"
        )
        productos_recientes = consultar(
            "SELECT p.nombre, u.nombre AS vendedor, c.nombre AS categoria, "
            "       p.precio, p.activo "
            "FROM producto p "
            "JOIN usuario u ON u.id = p.vendedor_id "
            "JOIN categoria c ON c.id = p.categoria_id "
            "ORDER BY p.id DESC LIMIT 6"
        )
        pedidos_recientes = consultar(
            "SELECT p.id, u.nombre AS cliente, p.total, p.estado, p.creado_en "
            "FROM pedido p JOIN usuario u ON u.id = p.cliente_id "
            "ORDER BY p.id DESC LIMIT 6"
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar todos los datos del panel.", "danger")

    return render_template(
        "dashboard.html",
        estadisticas=estadisticas,
        usuarios_recientes=usuarios_recientes,
        productos_recientes=productos_recientes,
        pedidos_recientes=pedidos_recientes
    )


@app.route("/admin/usuarios")
@admin_requerido
def admin_usuarios():
    rol = request.args.get("rol", "").strip()
    usuarios = []
    try:
        if rol in ("cliente", "vendedor", "domiciliario", "administrador"):
            usuarios = consultar(
                "SELECT id, nombre, correo, rol, activo, creado_en, ultimo_acceso "
                "FROM usuario WHERE rol = %s ORDER BY id DESC", (rol,)
            )
        else:
            rol = ""
            usuarios = consultar(
                "SELECT id, nombre, correo, rol, activo, creado_en, ultimo_acceso "
                "FROM usuario ORDER BY id DESC"
            )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los usuarios.", "danger")
    return render_template("admin_usuarios.html", usuarios=usuarios, rol_activo=rol)


@app.route("/admin/usuarios/<int:usuario_id>/estado", methods=["POST"])
@admin_requerido
def admin_usuario_estado(usuario_id):
    if usuario_id == session["usuario_id"]:
        flash("No puedes desactivar tu propia cuenta.", "warning")
        return redirect(request.referrer or url_for("admin_usuarios"))
    filas = ejecutar(
        "UPDATE usuario SET activo = 1 - activo WHERE id = %s", (usuario_id,)
    )
    if filas == 0:
        abort(404)
    flash("Actualizamos el estado de la cuenta.", "success")
    return redirect(url_for("admin_usuarios", rol=request.form.get("rol", "")))


@app.route("/admin/productos")
@admin_requerido
def admin_productos():
    productos = []
    try:
        productos = consultar(
            "SELECT p.id, p.nombre, p.precio, p.activo, p.imagen, p.creado_en, "
            "       u.nombre AS vendedor, c.nombre AS categoria "
            "FROM producto p "
            "JOIN usuario u ON u.id = p.vendedor_id "
            "JOIN categoria c ON c.id = p.categoria_id "
            "ORDER BY p.id DESC"
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los productos.", "danger")
    return render_template("admin_productos.html", productos=productos)


@app.route("/admin/productos/<int:producto_id>/estado", methods=["POST"])
@admin_requerido
def admin_producto_estado(producto_id):
    if ejecutar(
        "UPDATE producto SET activo = 1 - activo WHERE id = %s", (producto_id,)
    ) == 0:
        abort(404)
    flash("Actualizamos la visibilidad del producto.", "success")
    return redirect(url_for("admin_productos"))


@app.route("/admin/productos/<int:producto_id>/eliminar", methods=["POST"])
@admin_requerido
def admin_producto_eliminar(producto_id):
    producto = consultar(
        "SELECT imagen FROM producto WHERE id = %s", (producto_id,), uno=True
    )
    if producto is None:
        abort(404)
    ejecutar("DELETE FROM producto WHERE id = %s", (producto_id,))
    quitar_imagen(producto["imagen"])
    flash("Producto eliminado.", "success")
    return redirect(url_for("admin_productos"))


def crear_slug(texto):
    base = unicodedata.normalize("NFKD", texto.lower())
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


@app.route("/admin/categorias", methods=["GET", "POST"])
@admin_requerido
def admin_categorias():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        slug = crear_slug(nombre)
        if not nombre or not slug or len(nombre) > 60:
            flash("Escribe un nombre válido (máximo 60 caracteres).", "danger")
        else:
            try:
                ejecutar(
                    "INSERT INTO categoria (nombre, slug) VALUES (%s, %s)",
                    (nombre, slug)
                )
                flash(f"Categoría «{nombre}» creada.", "success")
            except pymysql.IntegrityError:
                flash("Ya existe una categoría con ese nombre.", "danger")
            except pymysql.MySQLError as error:
                app.logger.error("Error de MySQL: %s", error)
                flash("No pudimos crear la categoría.", "danger")
        return redirect(url_for("admin_categorias"))

    categorias = []
    try:
        categorias = consultar(
            "SELECT c.id, c.nombre, c.slug, COUNT(p.id) AS productos "
            "FROM categoria c LEFT JOIN producto p ON p.categoria_id = c.id "
            "GROUP BY c.id, c.nombre, c.slug ORDER BY c.id"
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar las categorías.", "danger")
    return render_template("admin_categorias.html", categorias=categorias)


@app.route("/admin/categorias/<int:categoria_id>/eliminar", methods=["POST"])
@admin_requerido
def admin_categoria_eliminar(categoria_id):
    try:
        if ejecutar("DELETE FROM categoria WHERE id = %s", (categoria_id,)) == 0:
            abort(404)
        flash("Categoría eliminada.", "success")
    except pymysql.IntegrityError:
        flash("No se puede eliminar: todavía tiene productos.", "danger")
    return redirect(url_for("admin_categorias"))


@app.route("/admin/pedidos")
@admin_requerido
def admin_pedidos():
    estado = request.args.get("estado", "").strip()
    pedidos, items = [], {}
    try:
        base = (
            "SELECT p.id, p.tipo_entrega, p.direccion, p.notas, p.total, "
            "       p.estado, p.creado_en, u.nombre AS cliente, u.correo "
            "FROM pedido p JOIN usuario u ON u.id = p.cliente_id "
        )
        if estado in ESTADOS_PEDIDO:
            pedidos = consultar(base + "WHERE p.estado = %s ORDER BY p.id DESC", (estado,))
        else:
            estado = ""
            pedidos = consultar(base + "ORDER BY p.id DESC")
        for it in consultar(
            "SELECT pedido_id, nombre, precio_unitario, cantidad "
            "FROM pedido_item ORDER BY id"
        ):
            items.setdefault(it["pedido_id"], []).append(it)
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los pedidos.", "danger")
    return render_template(
        "admin_pedidos.html", pedidos=pedidos, items=items,
        estados=ESTADOS_PEDIDO, estado_activo=estado
    )


@app.route("/admin/pedidos/<int:pedido_id>/estado", methods=["POST"])
@admin_requerido
def admin_pedido_estado(pedido_id):
    estado = request.form.get("estado", "")
    if estado not in ESTADOS_PEDIDO:
        abort(400)
    if ejecutar(
        "UPDATE pedido SET estado = %s WHERE id = %s", (estado, pedido_id)
    ) == 0:
        # rowcount 0 también ocurre si el estado ya era el mismo.
        if consultar("SELECT id FROM pedido WHERE id = %s", (pedido_id,), uno=True) is None:
            abort(404)
    flash(f"Pedido #{pedido_id} actualizado a «{estado}».", "success")
    return redirect(url_for("admin_pedidos", estado=request.form.get("filtro", "")))


# 19. PÁGINAS QUE TODAVÍA ESTÁN PENDIENTES

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


# 20. MANEJO DE ERRORES

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


# 21. EJECUTAR LA APLICACIÓN

if __name__ == "__main__":
    app.run(debug=True)
