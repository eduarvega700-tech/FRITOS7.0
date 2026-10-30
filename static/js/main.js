
(function () {
    "use strict";

    /* =====================================================
       1. CONFIGURACIÓN DEL CARRITO
    ===================================================== */

    // Clave utilizada para guardar el carrito en el navegador.
    var CLAVE = "fritosTechCarrito";


    /* =====================================================
       2. LEER Y GUARDAR EL CARRITO
    ===================================================== */

    // Obtener los productos guardados.
    function leer() {
        try {
            return JSON.parse(localStorage.getItem(CLAVE)) || {};
        } catch (e) {
            return {};
        }
    }

    // Guardar los productos en el navegador.
    function guardar(carrito) {
        try {
            localStorage.setItem(CLAVE, JSON.stringify(carrito));
        } catch (e) {
            // Continúa funcionando aunque el almacenamiento no esté disponible.
        }
    }

    // Calcular la cantidad total de productos.
    function total(carrito) {
        return Object.keys(carrito).reduce(function (suma, id) {
            return suma + carrito[id];
        }, 0);
    }


    /* =====================================================
       3. CONTADOR DEL CARRITO
    ===================================================== */

    var contador = document.getElementById("cart-count");

    // Actualizar el número que aparece en el carrito.
    function pintarContador() {
        var cantidad = total(leer());

        if (!contador) {
            return;
        }

        contador.textContent = cantidad;
        contador.hidden = cantidad === 0;
    }


    /* =====================================================
       4. SISTEMA DE AVISOS
    ===================================================== */

    var aviso = document.getElementById("aviso");
    var temporizador;

    // Mostrar un mensaje temporal en pantalla.
    function mostrarAviso(texto) {
        if (!aviso) {
            return;
        }

        aviso.textContent = texto;
        aviso.classList.add("aviso--visible");

        // Reiniciar el tiempo si ya había un aviso.
        clearTimeout(temporizador);

        temporizador = setTimeout(function () {
            aviso.classList.remove("aviso--visible");
        }, 2200);
    }


    /* =====================================================
       5. EVENTOS GENERALES DE LA PÁGINA
    ===================================================== */

    document.addEventListener("click", function (e) {

        /* -----------------------------------------------
           5.1. AGREGAR PRODUCTOS AL CARRITO
        ----------------------------------------------- */

        var agregar = e.target.closest("[data-add]");

        if (agregar) {
            var carrito = leer();
            var id = agregar.getAttribute("data-add");

            // Sumar una unidad del producto seleccionado (máximo 50).
            carrito[id] = Math.min((carrito[id] || 0) + 1, 50);

            guardar(carrito);
            pintarContador();

            // Mostrar la confirmación.
            var nombre = agregar.getAttribute("data-nombre");

            mostrarAviso(
                (nombre || "Producto") + " agregado al carrito"
            );

            return;
        }


        /* -----------------------------------------------
           5.2. MARCAR O DESMARCAR FAVORITOS
        ----------------------------------------------- */

        var favorito = e.target.closest(".btn-fav");

        if (favorito) {
            var activo = favorito.getAttribute("aria-pressed") === "true";

            favorito.setAttribute(
                "aria-pressed",
                String(!activo)
            );

            return;
        }


        /* -----------------------------------------------
           5.3. MOSTRAR U OCULTAR CONTRASEÑAS
        ----------------------------------------------- */

        var ver = e.target.closest("[data-ver-clave]");

        if (ver) {
            var campo = document.getElementById(
                ver.getAttribute("data-ver-clave")
            );

            // Comprobar que el campo exista.
            if (!campo) {
                return;
            }

            var visible = campo.type === "text";

            // Cambiar el tipo del campo.
            campo.type = visible ? "password" : "text";

            // Actualizar el estado accesible del botón.
            ver.setAttribute(
                "aria-pressed",
                String(!visible)
            );

            ver.setAttribute(
                "aria-label",
                visible ? "Mostrar contraseña" : "Ocultar contraseña"
            );

            // Cambiar el icono de Bootstrap Icons.
            if (ver.firstElementChild) {
                ver.firstElementChild.className = visible
                    ? "bi bi-eye-slash"
                    : "bi bi-eye";
            }

            return;
        }


        /* -----------------------------------------------
           5.4. BOTONES DE FUNCIONES PRÓXIMAS
        ----------------------------------------------- */

        if (e.target.closest("[data-proximamente]")) {
            mostrarAviso("Próximamente");
            return;
        }

    });


    /* =====================================================
       6. FILTRO DE PRODUCTOS POPULARES
    ===================================================== */

    var grilla = document.getElementById("grilla-populares");

    // Ejecutar el filtro solo si existe la grilla.
    if (grilla) {

        // Obtener los productos que contiene la grilla.
        var items = Array.prototype.slice.call(grilla.children);

        // Obtener los botones de filtro.
        var chips = document.querySelectorAll("[data-filtro]");

        // Mensaje para cuando no haya resultados.
        var vacio = document.getElementById("sin-resultados");

        // Máximo de productos visibles.
        var MAXIMO = 4;


        /* -----------------------------------------------
           6.1. FILTRAR LOS PRODUCTOS
        ----------------------------------------------- */

        function filtrar(slug) {
            var visibles = 0;

            items.forEach(function (producto) {

                // Comprobar si pertenece a la categoría seleccionada.
                var coincide =
                    slug === "todos" ||
                    producto.getAttribute("data-categoria") === slug;

                // Mostrar como máximo cuatro productos.
                var mostrar = coincide && visibles < MAXIMO;

                if (mostrar) {
                    visibles++;
                }

                // Ocultar los productos que no coinciden.
                producto.classList.toggle("d-none", !mostrar);
            });

            // Mostrar el mensaje si no hay resultados.
            if (vacio) {
                vacio.hidden = visibles > 0;
            }
        }


        /* -----------------------------------------------
           6.2. EVENTOS DE LOS BOTONES DE FILTRO
        ----------------------------------------------- */

        chips.forEach(function (chip) {

            chip.addEventListener("click", function () {

                // Actualizar cuál filtro está seleccionado.
                chips.forEach(function (otroChip) {
                    var seleccionado = otroChip === chip;

                    otroChip.classList.toggle(
                        "chip--activo",
                        seleccionado
                    );

                    otroChip.setAttribute(
                        "aria-pressed",
                        String(seleccionado)
                    );
                });

                // Filtrar por la categoría seleccionada.
                filtrar(chip.getAttribute("data-filtro"));
            });

        });


        /* -----------------------------------------------
           6.3. FILTRO INICIAL
        ----------------------------------------------- */

        // Mostrar todos los productos al cargar la página,
        // respetando el límite máximo de cuatro.
        filtrar("todos");
    }


    /* =====================================================
       7. PÁGINA DEL CARRITO (/carrito)
    ===================================================== */

    var pagina = document.getElementById("carrito-pagina");

    if (pagina) {
        var csrf = pagina.getAttribute("data-csrf");
        var maxUnidades = parseInt(pagina.getAttribute("data-max"), 10) || 50;

        var elLista = document.getElementById("carrito-lista");
        var elContenido = document.getElementById("carrito-contenido");
        var elVacio = document.getElementById("carrito-vacio");
        var elError = document.getElementById("carrito-error");
        var elCargando = document.getElementById("carrito-cargando");
        var elUnidades = document.getElementById("carrito-unidades");
        var elTotal = document.getElementById("carrito-total");
        var elItems = document.getElementById("carrito-items");
        var elForm = document.getElementById("carrito-form");
        var elDireccion = document.getElementById("bloque-direccion");
        var inputDireccion = document.getElementById("c-direccion");

        // Datos de los productos que devolvió el servidor.
        var productos = [];

        // Formato de pesos colombianos: 2500 -> $2.500
        function cop(valor) {
            return "$" + String(Math.round(valor))
                .replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        }

        function crear(etiqueta, clase, texto) {
            var el = document.createElement(etiqueta);
            if (clase) { el.className = clase; }
            if (texto !== undefined) { el.textContent = texto; }
            return el;
        }

        // Dibuja la lista y los totales a partir de `productos`.
        function pintarCarrito() {
            elLista.innerHTML = "";
            var unidades = 0;
            var suma = 0;

            productos.forEach(function (p) {
                unidades += p.cantidad;
                suma += p.precio * p.cantidad;

                var li = crear("li", "carrito-item");

                var img = crear("img", "carrito-item__img");
                img.src = p.img;
                img.alt = p.nombre;
                img.loading = "lazy";
                li.appendChild(img);

                var info = crear("div", "carrito-item__info");
                info.appendChild(crear("h3", "carrito-item__nombre", p.nombre));
                info.appendChild(crear("p", "carrito-item__vendedor", p.vendedor));
                info.appendChild(crear("p", "carrito-item__precio", cop(p.precio) + " PESOS"));
                li.appendChild(info);

                var acciones = crear("div", "carrito-item__acciones");

                var cantidad = crear("div", "carrito-cantidad");
                var menos = crear("button", "", "−");
                menos.type = "button";
                menos.setAttribute("data-cambiar", p.id + ":-1");
                menos.setAttribute("aria-label", "Quitar una unidad de " + p.nombre);
                var num = crear("span", "", String(p.cantidad));
                var mas = crear("button", "", "+");
                mas.type = "button";
                mas.setAttribute("data-cambiar", p.id + ":1");
                mas.setAttribute("aria-label", "Agregar una unidad de " + p.nombre);
                mas.disabled = p.cantidad >= maxUnidades;
                cantidad.appendChild(menos);
                cantidad.appendChild(num);
                cantidad.appendChild(mas);
                acciones.appendChild(cantidad);

                acciones.appendChild(
                    crear("strong", "carrito-item__subtotal", cop(p.precio * p.cantidad))
                );

                var quitar = crear("button", "carrito-item__quitar");
                quitar.type = "button";
                quitar.setAttribute("data-quitar", p.id);
                quitar.setAttribute("aria-label", "Quitar " + p.nombre + " del carrito");
                var icono = crear("i", "bi bi-x-lg");
                icono.setAttribute("aria-hidden", "true");
                quitar.appendChild(icono);
                acciones.appendChild(quitar);

                li.appendChild(acciones);
                elLista.appendChild(li);
            });

            elUnidades.textContent = String(unidades);
            elTotal.textContent = cop(suma);

            var vacio = productos.length === 0;
            elContenido.hidden = vacio;
            elVacio.hidden = !vacio;
        }

        // Pide al servidor los datos reales de lo que hay en el carrito.
        function cargarCarrito() {
            var guardado = leer();

            if (Object.keys(guardado).length === 0) {
                elCargando.hidden = true;
                productos = [];
                pintarCarrito();
                return;
            }

            fetch("/api/carrito", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": csrf
                },
                body: JSON.stringify({ items: guardado })
            })
                .then(function (r) {
                    if (!r.ok) { throw new Error("http " + r.status); }
                    return r.json();
                })
                .then(function (datos) {
                    productos = datos.productos || [];

                    // Quitar del navegador los productos que ya no existen.
                    var vigente = {};
                    productos.forEach(function (p) { vigente[p.id] = p.cantidad; });
                    if (Object.keys(vigente).length !== Object.keys(guardado).length) {
                        guardar(vigente);
                        pintarContador();
                        mostrarAviso("Quitamos productos que ya no están disponibles");
                    }

                    elCargando.hidden = true;
                    pintarCarrito();
                })
                .catch(function () {
                    elCargando.hidden = true;
                    elError.hidden = false;
                });
        }

        // Cambiar la cantidad o quitar un producto.
        pagina.addEventListener("click", function (e) {
            var cambio = e.target.closest("[data-cambiar]");
            var quitar = e.target.closest("[data-quitar]");
            var vaciar = e.target.closest("#carrito-vaciar");
            var carrito = leer();

            if (cambio) {
                var partes = cambio.getAttribute("data-cambiar").split(":");
                var id = partes[0];
                var nueva = (carrito[id] || 0) + parseInt(partes[1], 10);

                if (nueva <= 0) {
                    delete carrito[id];
                } else {
                    carrito[id] = Math.min(nueva, maxUnidades);
                }
            } else if (quitar) {
                delete carrito[quitar.getAttribute("data-quitar")];
            } else if (vaciar) {
                carrito = {};
            } else {
                return;
            }

            guardar(carrito);
            pintarContador();

            // Actualizar la vista sin volver a pedir datos.
            productos = productos
                .filter(function (p) { return carrito[p.id]; })
                .map(function (p) {
                    p.cantidad = carrito[p.id];
                    return p;
                });
            pintarCarrito();
        });

        // Mostrar el campo de dirección solo si es a domicilio.
        function actualizarEntrega() {
            var domicilio = document.getElementById("t-domicilio").checked;
            elDireccion.hidden = !domicilio;
            inputDireccion.required = domicilio;
        }

        Array.prototype.forEach.call(
            document.querySelectorAll("input[name='tipo_entrega']"),
            function (radio) { radio.addEventListener("change", actualizarEntrega); }
        );

        // Al enviar, mandar el contenido del carrito junto al formulario.
        elForm.addEventListener("submit", function () {
            elItems.value = JSON.stringify(leer());
        });

        actualizarEntrega();
        cargarCarrito();
    }


    /* =====================================================
       8. VACIAR EL CARRITO TRAS UN PEDIDO EXITOSO
    ===================================================== */

    if (document.querySelector("[data-vaciar-carrito]")) {
        guardar({});
    }


    /* =====================================================
       9. INICIALIZACIÓN
    ===================================================== */

    // Actualizar el contador al cargar el JavaScript.
    pintarContador();

})();

const botonTema = document.getElementById("botonTema");

const temaGuardado = localStorage.getItem("tema-fritos") || "light";

function aplicarTema(tema) {
    document.body.setAttribute("data-theme", tema);

    if (botonTema) {
        const modoNoche = tema === "dark";

        botonTema.setAttribute(
            "aria-label",
            modoNoche ? "Activar modo día" : "Activar modo noche"
        );

        botonTema.setAttribute("aria-pressed", String(modoNoche));
    }
}

if (botonTema) {
    botonTema.addEventListener("click", function () {
        const temaActual = document.body.getAttribute("data-theme");

        const nuevoTema = temaActual === "dark" ? "light" : "dark";

        aplicarTema(nuevoTema);

        localStorage.setItem("tema-fritos", nuevoTema);
    });
}

aplicarTema(temaGuardado);
