# 1. IMPORTACIONES

import hmac
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
    # El vendedor entra a su panel; los demás a explorar.
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
def cliente_requerido(vista):
    @wraps(vista)
    def interior(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Inicia sesión como cliente para continuar.", "info")
            return redirect(url_for("acceso_rol", rol="cliente"))
        if session.get("rol") != "cliente":
            flash("Esta sección es solo para clientes.", "warning")
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
# 11.1 CATALOGO DE PUESTOS
@app.route("/puestos")
def puestos():
    lista = []
    try:
        lista = consultar(
            "SELECT pu.vendedor_id AS id, pu.nombre, pu.barrio, pu.ciudad, "
            "       pu.horario, pu.abierto, pu.acepta_domicilio, "
            "       pu.costo_domicilio, COUNT(p.id) AS n_productos "
            "FROM puesto pu "
            "JOIN usuario u ON u.id = pu.vendedor_id AND u.activo = 1 "
            "LEFT JOIN producto p "
            "       ON p.vendedor_id = pu.vendedor_id AND p.activo = 1 "
            "GROUP BY pu.vendedor_id "
            "ORDER BY pu.abierto DESC, pu.nombre"
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar los puestos. Revisa la base de datos.", "danger")

    return render_template("puestos.html", puestos=lista)

@app.route("/puestos/<int:puesto_id>")
def puesto_detalle(puesto_id):
    try:
        puesto = consultar(
            "SELECT pu.vendedor_id AS id, pu.nombre, pu.descripcion, "
            "       pu.direccion, pu.barrio, pu.ciudad, pu.horario, "
            "       pu.abierto, pu.acepta_domicilio, pu.costo_domicilio "
            "FROM puesto pu "
            "JOIN usuario u ON u.id = pu.vendedor_id AND u.activo = 1 "
            "WHERE pu.vendedor_id = %s",
            (puesto_id,),
            uno=True
        )

        # Si el puesto no existe, mostrar error 404.
        if puesto is None:
            abort(404)

        productos = consultar(
            "SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen, "
            "       p.disponible, c.nombre AS categoria "
            "FROM producto p "
            "JOIN categoria c ON c.id = p.categoria_id "
            "WHERE p.vendedor_id = %s AND p.activo = 1 "
            "ORDER BY c.id, p.nombre",
            (puesto_id,)
        )
    except pymysql.MySQLError as error:
        app.logger.error("Error de MySQL: %s", error)
        flash("No pudimos cargar ese puesto. Revisa la base de datos.", "danger")
        return redirect(url_for("puestos"))

    return render_template(
        "puesto_detalle.html",
        puesto=puesto,
        productos=productos
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
