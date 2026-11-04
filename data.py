"""
Datos de ejemplo para mostrar las categorías y los productos
en la página principal de FRITOS TECH.

Por ahora, los datos están escritos directamente en Python.
Cuando conectemos la base de datos, se reemplazarán por
consultas a las tablas categoria y producto.
"""


# 2. CATEGORÍAS DE PRODUCTOS

CATEGORIAS = [
    {
        "nombre": "Empanadas",
        "slug": "empanadas",
        "imagen": "empanadas.png"
    },
    {
        "nombre": "Arepas de huevo",
        "slug": "arepas-de-huevo",
        "imagen": "arepas.png"
    },
    {
        "nombre": "Carimañolas",
        "slug": "carimañola",
        "imagen": "carimañola.png"
    },
    {
        "nombre": "Patacones",
        "slug": "patacones",
        "imagen": "patacones.png"
    },
    {
        "nombre": "Buñuelos",
        "slug": "buñuelos",
        "imagen": "bunuelos.png"
    },
    {
        "nombre": "Otros",
        "slug": "otros",
        "imagen": "otros.png"
    }
]


# 3. CIUDAD DE LOS PRODUCTOS

_CIUDAD = "Cartagena, Bolívar"


# 4. LISTA DE PRODUCTOS

PRODUCTOS = [

    # PRODUCTO 1: EMPANADAS DE CARNE

    {
        "id": 1,
        "nombre": "Empanadas de carne",
        "vendedor": "La Delicia de la Abuela",
        "rating": 4.8,
        "resenas": 124,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": "Más vendido",
        "destacado": True,
        "categoria": "empanadas",
        "descripcion": "Empanadas crujientes de maíz rellenas de carne molida bien sazonada.",
        "emoji": "",
        "img": "prod-empanadas.jpg"
    },

    # PRODUCTO 2: AREPA DE HUEVO

    {
        "id": 2,
        "nombre": "Arepa de huevo",
        "vendedor": "Sabor Caribe",
        "rating": 4.9,
        "resenas": 98,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": "Nuevo",
        "destacado": True,
        "categoria": "arepas-de-huevo",
        "descripcion": "Arepa de maíz frita con un huevo entero en el centro, el clásico de la costa.",
        "emoji": "",
        "img": "prod-arepa.jpg"
    },

    # PRODUCTO 3: CARIMAÑOLAS DE YUCA

    {
        "id": 3,
        "nombre": "Carimañolas de yuca",
        "vendedor": "El Sabor del Caribe",
        "rating": 4.7,
        "resenas": 76,
        "ciudad": _CIUDAD,
        "precio": 2500,
        "etiqueta": "Más vendido",
        "destacado": True,
        "categoria": "carimañola",
        "descripcion": "Masa de yuca en forma de torpedo, rellena de carne y frita hasta dorar.",
        "emoji": "",
        "img": "prod-carimañola.jpg"
    },

    # PRODUCTO 4: PATACONES CON HOGAO

    {
        "id": 4,
        "nombre": "Patacones con hogao",
        "vendedor": "La Esquina del Sabor",
        "rating": 4.8,
        "resenas": 110,
        "ciudad": _CIUDAD,
        "precio": 3500,
        "etiqueta": "Popular",
        "destacado": True,
        "categoria": "patacones",
        "descripcion": "Plátano verde frito y aplastado, acompañado de hogao casero de tomate y cebolla.",
        "emoji": "",
        "img": "prod-patacones.jpg"
    },

    # PRODUCTO 5: BUÑUELOS

    {
        "id": 5,
        "nombre": "Buñuelos",
        "vendedor": "Doña Rosa Fritos",
        "rating": 4.6,
        "resenas": 52,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "buñuelos",
        "descripcion": "Bolitas de masa fritas, doradas por fuera y suaves por dentro.",
        "emoji": "",
        "img": "prod-bunuelos.jpg"
    },

    # PRODUCTO 6: EMPANADA DE POLLO

    {
        "id": 6,
        "nombre": "Empanada de pollo",
        "vendedor": "El Rincón Cartagenero",
        "rating": 4.7,
        "resenas": 88,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Empanada dorada rellena de pollo desmechado con un toque criollo.",
        "emoji": "",
        "img": "prod-empanada-pollo.jpg"
    },

    # PRODUCTO 7: AREPA DE HUEVO ESPECIAL

    {
        "id": 7,
        "nombre": "Arepa de huevo especial",
        "vendedor": "La Matrona",
        "rating": 4.8,
        "resenas": 64,
        "ciudad": _CIUDAD,
        "precio": 3500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "arepas-de-huevo",
        "descripcion": "Arepa de huevo con relleno extra, más grande y llena de sabor.",
        "emoji": "",
        "img": "prod-arepa-especial.jpg"
    },

    # PRODUCTO 8: PATACÓN CON QUESO

    {
        "id": 8,
        "nombre": "Patacón con queso",
        "vendedor": "Fritos Don Luis",
        "rating": 4.5,
        "resenas": 41,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "patacones",
        "descripcion": "Patacón crocante cubierto con queso costeño rallado.",
        "emoji": "",
        "img": "prod-patacon-queso.jpg"
    },

    # PRODUCTO 9: EMPANADAS DE QUESO

    {
        "id": 9,
        "nombre": "Empanadas de queso",
        "vendedor": "La Delicia de la Abuela",
        "rating": 4.7,
        "resenas": 58,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Masa de maíz crujiente rellena de queso costeño derretido.",
        "emoji": "",
        "img": "empanadas_de_queso.jpg"
    },

    # PRODUCTO 10: EMPANADAS DE PIPIÁN

    {
        "id": 10,
        "nombre": "Empanadas de pipián",
        "vendedor": "Sazón Andino",
        "rating": 4.6,
        "resenas": 33,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Empanadas de papa y maní al estilo de Nariño, servidas con ají.",
        "emoji": "",
        "img": "empanadas_pipian.jpg"
    },

    # PRODUCTO 11: EMPANADAS VALLECAUCANAS

    {
        "id": 11,
        "nombre": "Empanadas vallecaucanas",
        "vendedor": "El Rincón Cartagenero",
        "rating": 4.5,
        "resenas": 29,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Pequeñas empanadas de masa de maíz rellenas de carne y papa.",
        "emoji": "",
        "img": "empanadas_vallecaucanas.jpg"
    },

    # PRODUCTO 12: EMPANADAS DE CAMBRAY

    {
        "id": 12,
        "nombre": "Empanadas de cambray",
        "vendedor": "Fritos Don Luis",
        "rating": 4.6,
        "resenas": 47,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Empanadas de masa de trigo, doradas y rellenas de carne o queso.",
        "emoji": "",
        "img": "empanadas_cambray.jpg"
    },

    # PRODUCTO 13: EMPANADAS DE YUCA

    {
        "id": 13,
        "nombre": "Empanadas de yuca",
        "vendedor": "Sabor Caribe",
        "rating": 4.7,
        "resenas": 52,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Masa suave de yuca frita, rellena de queso o carne.",
        "emoji": "",
        "img": "empanadas_yuca.jpg"
    },

    # PRODUCTO 14: EMPANADAS DE CAMARÓN

    {
        "id": 14,
        "nombre": "Empanadas de camarón",
        "vendedor": "Mar y Sabor",
        "rating": 4.8,
        "resenas": 61,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "empanadas",
        "descripcion": "Empanadas crocantes rellenas de camarones guisados, típicas del Caribe.",
        "emoji": "",
        "img": "empanadas_camaron.jpg"
    },

    # PRODUCTO 15: AREPA DE HUEVO CON CARNE

    {
        "id": 15,
        "nombre": "Arepa de huevo con carne",
        "vendedor": "La Matrona",
        "rating": 4.8,
        "resenas": 73,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "arepas-de-huevo",
        "descripcion": "Arepa frita con huevo en el centro y relleno generoso de carne molida.",
        "emoji": "",
        "img": "arepa_huevo_carne.jpg"
    },

    # PRODUCTO 16: AREPA DE HUEVO CON QUESO

    {
        "id": 16,
        "nombre": "Arepa de huevo con queso",
        "vendedor": "Sabor Caribe",
        "rating": 4.7,
        "resenas": 55,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "arepas-de-huevo",
        "descripcion": "Arepa de huevo crujiente con mucho queso costeño derretido por dentro.",
        "emoji": "",
        "img": "arepa_huevo_queso.jpg"
    },

    # PRODUCTO 17: CARIMAÑOLAS DE QUESO

    {
        "id": 17,
        "nombre": "Carimañolas de queso",
        "vendedor": "El Sabor del Caribe",
        "rating": 4.7,
        "resenas": 44,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "carimañola",
        "descripcion": "Masa de yuca frita rellena de queso suave que se derrite al morder.",
        "emoji": "",
        "img": "carimanolas_de_queso.jpg"
    },

    # PRODUCTO 18: PATACÓN PISAO

    {
        "id": 18,
        "nombre": "Patacón pisao",
        "vendedor": "La Esquina del Sabor",
        "rating": 4.8,
        "resenas": 69,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "patacones",
        "descripcion": "Plátano verde aplastado y frito dos veces, crocante y con sal justa.",
        "emoji": "",
        "img": "patacon_pisao.jpg"
    },

    # PRODUCTO 19: BUÑUELOS DE FRIJOL

    {
        "id": 19,
        "nombre": "Buñuelos de frijol",
        "vendedor": "Doña Rosa Fritos",
        "rating": 4.6,
        "resenas": 38,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "buñuelos",
        "descripcion": "Buñuelos del Caribe hechos con frijol cabecita negra, dorados y sabrosos.",
        "emoji": "",
        "img": "bunuelos_frijol.jpg"
    },

    # PRODUCTO 20: PAPA RELLENA

    {
        "id": 20,
        "nombre": "Papa rellena",
        "vendedor": "El Rincón Cartagenero",
        "rating": 4.7,
        "resenas": 60,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Bola de papa rellena de carne guisada, frita hasta quedar dorada.",
        "emoji": "",
        "img": "papa_rellena.jpg"
    },

    # PRODUCTO 21: DEDITOS DE QUESO

    {
        "id": 21,
        "nombre": "Deditos de queso",
        "vendedor": "Fritos Don Luis",
        "rating": 4.5,
        "resenas": 36,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Bastones de masa rellenos de queso que se derrite al morderlos.",
        "emoji": "",
        "img": "deditos_queso.jpg"
    },

    # PRODUCTO 22: MARRANITAS

    {
        "id": 22,
        "nombre": "Marranitas",
        "vendedor": "La Delicia de la Abuela",
        "rating": 4.6,
        "resenas": 42,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Plátano maduro frito relleno de chicharrón, dulce y salado a la vez.",
        "emoji": "",
        "img": "marranitas.jpg"
    },

    # PRODUCTO 23: ABORRAJADOS

    {
        "id": 23,
        "nombre": "Aborrajados",
        "vendedor": "Sazón Andino",
        "rating": 4.8,
        "resenas": 57,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Plátano maduro con queso, apanado y frito hasta quedar crujiente.",
        "emoji": "",
        "img": "aborrajados.jpg"
    },

    # PRODUCTO 24: QUIBBES

    {
        "id": 24,
        "nombre": "Quibbes",
        "vendedor": "Sabor Caribe",
        "rating": 4.7,
        "resenas": 49,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Croquetas de trigo y carne con especias, herencia árabe del Caribe.",
        "emoji": "",
        "img": "quibbes.jpg"
    },

    # PRODUCTO 25: PASTEL DE POLLO

    {
        "id": 25,
        "nombre": "Pastel de pollo",
        "vendedor": "El Rincón Cartagenero",
        "rating": 4.6,
        "resenas": 35,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Pastel hojaldrado y dorado relleno de pollo guisado con verduras.",
        "emoji": "",
        "img": "pastel_pollo.jpg"
    },

    # PRODUCTO 26: YUCA FRITA

    {
        "id": 26,
        "nombre": "Yuca frita",
        "vendedor": "Doña Rosa Fritos",
        "rating": 4.5,
        "resenas": 31,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Bastones de yuca fritos, crujientes por fuera y suaves por dentro.",
        "emoji": "",
        "img": "yuca_frita.jpg"
    },

    # PRODUCTO 27: TAJADAS DE PLÁTANO MADURO

    {
        "id": 27,
        "nombre": "Tajadas de plátano maduro",
        "vendedor": "La Esquina del Sabor",
        "rating": 4.6,
        "resenas": 40,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Rodajas de plátano maduro fritas, caramelizadas y dulces.",
        "emoji": "",
        "img": "tajadas_platano_maduro.jpg"
    },

    # PRODUCTO 28: PAPAS CRIOLLAS FRITAS

    {
        "id": 28,
        "nombre": "Papas criollas fritas",
        "vendedor": "Fritos Don Luis",
        "rating": 4.5,
        "resenas": 28,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Papitas criollas amarillas fritas enteras, doradas y con sal.",
        "emoji": "",
        "img": "papas_criollas_fritas.jpg"
    },

    # PRODUCTO 29: CHICHARRÓN

    {
        "id": 29,
        "nombre": "Chicharrón",
        "vendedor": "La Matrona",
        "rating": 4.8,
        "resenas": 66,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Trozos de cerdo fritos, bien crocantes por fuera y jugosos por dentro.",
        "emoji": "",
        "img": "chicharron.jpg"
    },

    # PRODUCTO 30: PASTELES DE YUCA

    {
        "id": 30,
        "nombre": "Pasteles de yuca",
        "vendedor": "El Sabor del Caribe",
        "rating": 4.6,
        "resenas": 37,
        "ciudad": _CIUDAD,
        "precio": 2000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Pasteles de masa de yuca rellenos de carne o queso, fritos al momento.",
        "emoji": "",
        "img": "pasteles_yuca.jpg"
    },

    # PRODUCTO 31: AREPA FRITA

    {
        "id": 31,
        "nombre": "Arepa frita",
        "vendedor": "Sabor Caribe",
        "rating": 4.5,
        "resenas": 30,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Arepa de maíz frita, inflada y dorada, perfecta para acompañar.",
        "emoji": "",
        "img": "arepa_frita.jpg"
    },

    # PRODUCTO 32: HOJALDRAS

    {
        "id": 32,
        "nombre": "Hojaldras",
        "vendedor": "Sazón Andino",
        "rating": 4.6,
        "resenas": 34,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Masa de trigo frita, aireada y ligera, ideal para el desayuno.",
        "emoji": "",
        "img": "hojaldras.jpg"
    },

    # PRODUCTO 33: BOLITAS DE YUCA CON QUESO

    {
        "id": 33,
        "nombre": "Bolitas de yuca con queso",
        "vendedor": "Doña Rosa Fritos",
        "rating": 4.7,
        "resenas": 46,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Bolitas de yuca rellenas de queso, crujientes y bien suaves por dentro.",
        "emoji": "",
        "img": "bolitas_yuca_queso.jpg"
    },

    # PRODUCTO 34: AREPA DE CHOCLO FRITA

    {
        "id": 34,
        "nombre": "Arepa de choclo frita",
        "vendedor": "La Matrona",
        "rating": 4.7,
        "resenas": 43,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Arepa de maíz tierno frita, ligeramente dulce y con queso.",
        "emoji": "",
        "img": "arepa_choclo_frita.jpg"
    },

    # PRODUCTO 35: CAZÓN FRITO

    {
        "id": 35,
        "nombre": "Cazón frito",
        "vendedor": "Mar y Sabor",
        "rating": 4.6,
        "resenas": 32,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Trozos de cazón apanados y fritos, frescos del mar Caribe.",
        "emoji": "",
        "img": "cazon_frito.jpg"
    },

    # PRODUCTO 36: PLÁTANO RELLENO FRITO

    {
        "id": 36,
        "nombre": "Plátano relleno frito",
        "vendedor": "La Esquina del Sabor",
        "rating": 4.7,
        "resenas": 39,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Plátano frito relleno de carne o queso, dulce por fuera y sabroso por dentro.",
        "emoji": "",
        "img": "platano_relleno_frito.jpg"
    },

    # PRODUCTO 37: TOSTADAS DE PLÁTANO VERDE

    {
        "id": 37,
        "nombre": "Tostadas de plátano verde",
        "vendedor": "Fritos Don Luis",
        "rating": 4.5,
        "resenas": 27,
        "ciudad": _CIUDAD,
        "precio": 1500,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Láminas finas de plátano verde fritas, crocantes y saladas.",
        "emoji": "",
        "img": "tostadas_platano_verde.jpg"
    },

    # PRODUCTO 38: PAPA RELLENA CON ARROZ Y HUEVO

    {
        "id": 38,
        "nombre": "Papa rellena con arroz y huevo",
        "vendedor": "El Rincón Cartagenero",
        "rating": 4.8,
        "resenas": 51,
        "ciudad": _CIUDAD,
        "precio": 3000,
        "etiqueta": None,
        "destacado": False,
        "categoria": "otros",
        "descripcion": "Papa rellena con carne, arroz y huevo cocido, una versión más contundente.",
        "emoji": "",
        "img": "papa_rellena_arroz_huevo.jpg"
    }

]


# 5. PRODUCTOS DESTACADOS

PRODUCTOS_DESTACADOS = [
    producto
    for producto in PRODUCTOS
    if producto["destacado"]
]
