
from flask import Blueprint, render_template, request, abort

from data import CATEGORIAS, PRODUCTOS
from database import consultar
from models.producto import (
    obtener_categorias,
    obtener_productos,
)

catalogo_bp = Blueprint("catalogo", __name__)


def cargar_catalogo(slug=""):
    """Carga el catálogo desde MySQL o utiliza los datos de demostración."""
    try:
        categorias = obtener_categorias(consultar)
        productos = obtener_productos(consultar, slug)

        if not categorias:
            categorias = CATEGORIAS

        return categorias, productos

    except Exception:
        categorias = CATEGORIAS

        if slug:
            productos = [
                producto
                for producto in PRODUCTOS
                if producto.get("categoria") == slug
            ]
        else:
            productos = PRODUCTOS

        return categorias, productos


@catalogo_bp.route("/explorar")
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
