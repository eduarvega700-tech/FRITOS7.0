/* Buscador del navbar + filtrado en Explorar */
(function () {
  var form = document.getElementById('form-buscador');
  if (!form) return;

  var input = document.getElementById('buscador-input');
  var boton = document.getElementById('buscador-boton');
  var grilla = document.getElementById('grilla-explorar');   // solo existe en Explorar
  var resumen = document.getElementById('busqueda-resumen');
  var vacia = document.getElementById('busqueda-vacia');

  // Minúsculas y sin tildes: "buñuelos" == "bunuelos"
  function limpiar(s) {
    return (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }

  function abrir() {
    form.classList.add('buscador--abierto');
    boton.setAttribute('aria-expanded', 'true');
    input.focus();
  }

  function cerrar() {
    form.classList.remove('buscador--abierto');
    boton.setAttribute('aria-expanded', 'false');
  }

  // Filtra las tarjetas de Explorar (todas las palabras deben aparecer)
  function filtrar() {
    if (!grilla) return;
    var texto = input.value.trim();
    var palabras = limpiar(texto).split(/\s+/).filter(Boolean);
    var tarjetas = grilla.querySelectorAll('[data-buscar]');
    var visibles = 0;

    tarjetas.forEach(function (t) {
      var base = limpiar(t.getAttribute('data-buscar'));
      var coincide = palabras.every(function (p) { return base.indexOf(p) !== -1; });
      t.hidden = !coincide;
      if (coincide) visibles++;
    });

    if (resumen) {
      resumen.hidden = !palabras.length;
      resumen.textContent = palabras.length
        ? visibles + ' resultado' + (visibles === 1 ? '' : 's') + ' para «' + texto + '»'
        : '';
    }
    if (vacia) vacia.hidden = !(palabras.length && visibles === 0);
  }

  boton.addEventListener('click', function (e) {
    var abierto = form.classList.contains('buscador--abierto');
    if (!abierto) { e.preventDefault(); abrir(); return; }          // 1.º clic: despliega
    if (!input.value.trim()) { e.preventDefault(); cerrar(); }       // vacío: se pliega
    // con texto: el formulario se envía a /explorar?q=...
  });

  form.addEventListener('submit', function (e) {
    if (!input.value.trim()) { e.preventDefault(); return; }
    if (grilla) { e.preventDefault(); filtrar(); }                   // en Explorar no recarga
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { cerrar(); boton.focus(); }
  });

  if (grilla) {
    input.addEventListener('input', function () {
      filtrar();
      // mantiene la URL compartible sin recargar
      var url = new URL(location.href);
      if (input.value.trim()) url.searchParams.set('q', input.value.trim());
      else url.searchParams.delete('q');
      history.replaceState(null, '', url);
    });
  }

  // Si llegamos con ?q=..., mostrar el campo abierto y aplicar el filtro
  if (input.value.trim()) { abrir(); filtrar(); }
})();
