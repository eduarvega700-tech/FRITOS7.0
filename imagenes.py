"""Fotos de los productos de ejemplo (las que usan index.html y explorar.html)."""

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


def ruta_imagen(nombre, imagen):
    """Ruta relativa a /static de la foto de un producto."""
    if imagen and imagen.startswith("uploads/"):
        return imagen
    return "img/" + IMAGENES_PRODUCTOS.get(nombre, "logito.png")
