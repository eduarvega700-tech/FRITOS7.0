(function () {
  const boton = document.getElementById('botonTema');
  if (!boton) return;

  const CLAVE = 'tema';

  function aplicar(oscuro) {
    document.body.classList.toggle('modo-noche', oscuro);
    boton.setAttribute('aria-pressed', String(oscuro));
    boton.setAttribute('aria-label', oscuro ? 'Activar modo día' : 'Activar modo noche');
    document.documentElement.setAttribute('data-bs-theme', oscuro ? 'dark' : 'light');
  }

  let guardado = null;
  try { guardado = localStorage.getItem(CLAVE); } catch (e) {}
  aplicar(guardado === 'oscuro');

  boton.addEventListener('click', function () {
    const oscuro = !document.body.classList.contains('modo-noche');
    aplicar(oscuro);
    try { localStorage.setItem(CLAVE, oscuro ? 'oscuro' : 'claro'); } catch (e) {}
  });
})();