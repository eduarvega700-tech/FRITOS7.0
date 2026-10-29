# FRITOS TECH · Portada (Iteración 0)

Maqueta funcional de la página de inicio con Flask, Bootstrap 5 y Tailwind.

## Ejecutar

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # http://127.0.0.1:5000
```

## Estructura

```
app.py                  rutas y filtros (formato de pesos COP)
data.py                 datos de EJEMPLO (categorías y productos)
templates/
  base.html             <head>, CDNs, navbar, footer
  index.html            portada
  explorar.html         listado con filtro por categoría
  proximamente.html     pantallas pendientes (login, registro, vender)
  partials/             _navbar, _footer, _macros (imagen con respaldo, tarjeta de producto)
static/css/styles.css   estilos propios (paleta, hero, tarjetas, ola del footer)
static/js/main.js       carrito de demostración, favoritos, filtro de populares
static/img/             tus imágenes (ver LEEME.txt)
```

## Cómo conviven Bootstrap y Tailwind

- **Bootstrap**: rejilla (`row`/`col-*`), navbar colapsable, botones base y comportamiento responsive.
- **Tailwind**: utilidades sueltas. Se carga con prefijo `tw-` (ej. `tw-py-20`) y con `preflight`
  desactivado para que no pise los estilos de Bootstrap.
- **styles.css**: identidad visual (colores, tipografías Poppins + Caveat) con variables CSS.
- El Tailwind por CDN es solo para desarrollo. Antes de publicar se compila con el CLI de Tailwind.

## Siguiente paso sugerido (Iteración 1 del documento)

Base de datos con SQLAlchemy, registro e inicio de sesión (RF-01.1 a RF-01.3) y roles.

#documento de fritostech

https://docs.google.com/document/d/1SXiBhyZGA23ZRbKBrWygoWokSMSrzmpu/edit?usp=sharing&ouid=105921561939046892503&rtpof=true&sd=true

