
/* Al tocar la foto de un producto se abre una ventana con su descripción */
(function () {

  var modalEl = document.getElementById('modalProducto');

  if (!modalEl || !window.bootstrap) return;

  var modal = bootstrap.Modal.getOrCreateInstance(modalEl);

  var $ = function (id) {
    return document.getElementById(id);
  };

  var ZONAS = '.producto__imagen, .tarjeta-producto__img';

  var tarjetaActual = null;


  // Obtiene el texto de un elemento dentro de la tarjeta
  function texto(card, selector) {
    var el = card.querySelector(selector);

    return el
      ? el.textContent.replace(/\s+/g, ' ').trim()
      : '';
  }


  // Marca como "clicables" solo las fotos de tarjetas que traen descripción
  document.querySelectorAll(ZONAS).forEach(function (zona) {

    var card = zona.closest('article');

    if (!card || !card.hasAttribute('data-det-desc')) return;

    var nombre = texto(
      card,
      '.producto__titulo, .tarjeta-producto__nombre'
    );

    zona.classList.add('detalle-clic');
    zona.setAttribute('role', 'button');
    zona.setAttribute('tabindex', '0');
    zona.setAttribute('aria-label', 'Ver detalles de ' + nombre);

  });


  // Abre la ventana con los detalles del producto
  function abrir(zona) {

    var card = zona.closest('article');

    tarjetaActual = card;

    var nombre = texto(
      card,
      '.producto__titulo, .tarjeta-producto__nombre'
    );

    var desc = (card.getAttribute('data-det-desc') || '').trim();

    var img = card.querySelector('img');


    // Información del producto
    $('modalProductoTitulo').textContent = nombre;

    $('modalProductoVendedor').textContent =
      texto(card, '.producto__vendedor, .tarjeta-producto__vendedor');

    $('modalProductoPrecio').textContent =
      texto(card, '.producto__precio, .tarjeta-producto__precio');

    $('modalProductoDesc').textContent =
      desc || 'Este producto todavía no tiene descripción.';


    // Imagen del producto
    $('modalProductoFoto').hidden = !img;

    if (img) {
      $('modalProductoImg').src = img.currentSrc || img.src;
      $('modalProductoImg').alt = nombre;
    }


    // Comprueba si la tarjeta tiene botón para agregar
    $('modalProductoAgregar').hidden =
      !card.querySelector('[data-add]');


    modal.show();

  }


  // Detecta los clics sobre las imágenes
  document.addEventListener('click', function (e) {

    var zona = e.target.closest('.detalle-clic');

    if (!zona || e.target.closest('button, a')) return;
    // Ej.: el corazón de favoritos

    abrir(zona);

  });


  // Permite abrir la ventana usando Enter o espacio
  document.addEventListener('keydown', function (e) {

    if (e.key !== 'Enter' && e.key !== ' ') return;

    if (
      !e.target.classList ||
      !e.target.classList.contains('detalle-clic')
    ) return;

    e.preventDefault();

    abrir(e.target);

  });


  // El botón de la ventana utiliza el mismo botón "Agregar" de la tarjeta
  $('modalProductoAgregar').addEventListener('click', function () {

    var boton = tarjetaActual &&
      tarjetaActual.querySelector('[data-add]');

    if (boton) boton.click();

    modal.hide();

  });

})();
