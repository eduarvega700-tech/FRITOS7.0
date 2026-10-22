-- =====================================================================
--  FRITOS TECH · Módulo del domiciliario (repartidor)
--  Motor: MySQL 8 / MariaDB 10.4+  ·  Base de datos: fritos_tech
--
--  Cómo ejecutarlo:
--     mysql -u root -p fritos_tech < repartidor.sql
--  o pégalo completo en MySQL Workbench / phpMyAdmin.
--
--  NO borra ni modifica tus tablas actuales (usuario, categoria,
--  producto, historial_acceso). Solo crea tablas nuevas.
--  Es seguro ejecutarlo varias veces (CREATE TABLE IF NOT EXISTS),
--  salvo la sección 6 (datos de ejemplo), que debes correr una sola vez.
--
--  ANTES DE EJECUTAR, revisa dos cosas:
--
--  (a) Tipo de usuario.id. Las llaves foráneas de abajo usan INT UNSIGNED.
--      Si tu tabla usuario usa INT normal, MySQL dará error 3780 / 1215.
--      Compruébalo con:   SHOW COLUMNS FROM usuario LIKE 'id';
--      y cambia INT UNSIGNED por INT (o al revés) en este archivo.
--
--  (b) Columna usuario.rol. Si es un ENUM que aún no incluye
--      'domiciliario', ejecuta (ajusta la lista a tus roles reales):
--        ALTER TABLE usuario MODIFY rol
--          ENUM('cliente','vendedor','domiciliario','administrador')
--          NOT NULL DEFAULT 'cliente';
-- =====================================================================

USE fritos_tech;

SET NAMES utf8mb4;


-- ---------------------------------------------------------------------
-- 1. REPARTIDOR: perfil del domiciliario (1 a 1 con usuario)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS repartidor (
    usuario_id             INT UNSIGNED NOT NULL,
    telefono               VARCHAR(20)  NULL,
    vehiculo               ENUM('moto','bicicleta','a_pie','carro')
                                        NOT NULL DEFAULT 'moto',
    placa                  VARCHAR(10)  NULL,
    disponible             TINYINT(1)   NOT NULL DEFAULT 0,
    latitud                DOUBLE       NULL,   -- última ubicación conocida
    longitud               DOUBLE       NULL,
    ubicacion_actualizada  DATETIME     NULL,
    creado_en              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id),
    CONSTRAINT fk_repartidor_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuario (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 2. LOCAL_VENDEDOR: dirección y coordenadas del local de cada vendedor
--    (de aquí sale el punto de recogida en el mapa)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS local_vendedor (
    vendedor_id   INT UNSIGNED  NOT NULL,
    nombre_local  VARCHAR(120)  NOT NULL,
    direccion     VARCHAR(200)  NOT NULL,
    barrio        VARCHAR(80)   NULL,
    telefono      VARCHAR(20)   NULL,
    latitud       DOUBLE        NULL,
    longitud      DOUBLE        NULL,
    creado_en     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vendedor_id),
    CONSTRAINT fk_local_vendedor
        FOREIGN KEY (vendedor_id) REFERENCES usuario (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 3. PEDIDO
--    Flujo de estados:
--      pendiente -> preparando -> listo -> asignado -> en_camino -> entregado
--                                  (repartidor acepta) (recoge)     (entrega)
--      cancelado puede ocurrir en cualquier momento.
--    costo_domicilio = lo que gana el repartidor por la entrega (COP).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido (
    id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    cliente_id         INT UNSIGNED NOT NULL,
    vendedor_id        INT UNSIGNED NOT NULL,
    repartidor_id      INT UNSIGNED NULL,
    estado             ENUM('pendiente','preparando','listo','asignado',
                            'en_camino','entregado','cancelado')
                                    NOT NULL DEFAULT 'pendiente',
    direccion_entrega  VARCHAR(200) NOT NULL,
    barrio             VARCHAR(80)  NULL,
    referencia         VARCHAR(200) NULL,        -- "casa blanca, portón negro"
    telefono_contacto  VARCHAR(20)  NULL,
    latitud            DOUBLE       NULL,        -- destino de la entrega
    longitud           DOUBLE       NULL,
    metodo_pago        ENUM('efectivo','transferencia','tarjeta')
                                    NOT NULL DEFAULT 'efectivo',
    total              INT UNSIGNED NOT NULL DEFAULT 0,   -- productos (COP)
    costo_domicilio    INT UNSIGNED NOT NULL DEFAULT 0,   -- ganancia repartidor
    notas              VARCHAR(255) NULL,
    creado_en          DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    aceptado_en        DATETIME     NULL,
    recogido_en        DATETIME     NULL,
    entregado_en       DATETIME     NULL,
    PRIMARY KEY (id),
    KEY idx_pedido_repartidor_estado (repartidor_id, estado),
    KEY idx_pedido_estado (estado, repartidor_id),
    KEY idx_pedido_vendedor (vendedor_id),
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (cliente_id)    REFERENCES usuario (id),
    CONSTRAINT fk_pedido_vendedor
        FOREIGN KEY (vendedor_id)   REFERENCES usuario (id),
    CONSTRAINT fk_pedido_repartidor
        FOREIGN KEY (repartidor_id) REFERENCES usuario (id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 4. PEDIDO_DETALLE: los fritos de cada pedido
--    Guarda copia del nombre y del precio para que el historial no
--    cambie si el vendedor edita o elimina el producto después.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_detalle (
    id               INT UNSIGNED NOT NULL AUTO_INCREMENT,
    pedido_id        INT UNSIGNED NOT NULL,
    producto_id      INT UNSIGNED NULL,
    nombre           VARCHAR(120) NOT NULL,
    cantidad         SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    precio_unitario  INT UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    KEY idx_detalle_pedido (pedido_id),
    CONSTRAINT fk_detalle_pedido
        FOREIGN KEY (pedido_id) REFERENCES pedido (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 5. Crear el perfil de repartidor para los domiciliarios ya registrados
--    (los nuevos se crean solos la primera vez que entran al panel)
-- ---------------------------------------------------------------------
INSERT IGNORE INTO repartidor (usuario_id)
SELECT id FROM usuario WHERE rol = 'domiciliario';


-- ---------------------------------------------------------------------
-- 6. DATOS DE EJEMPLO (OPCIONAL · ejecutar UNA sola vez)
--    Usa el primer vendedor y el primer cliente que existan en tu
--    base de datos. Si no hay alguno de los dos, no inserta nada.
--    Coordenadas reales de Cartagena para probar el mapa.
--    Para quitarlos:  DELETE FROM pedido WHERE notas LIKE '[demo]%';
-- ---------------------------------------------------------------------
SET @vendedor = (SELECT id FROM usuario WHERE rol = 'vendedor'
                 ORDER BY id LIMIT 1);
SET @cliente  = (SELECT id FROM usuario WHERE rol = 'cliente'
                 ORDER BY id LIMIT 1);

INSERT IGNORE INTO local_vendedor
    (vendedor_id, nombre_local, direccion, barrio, telefono, latitud, longitud)
SELECT id, CONCAT('Fritos de ', nombre), 'Calle del Arsenal #8-29',
       'Getsemaní', '3001112233', 10.42180, -75.54720
FROM usuario
WHERE id = @vendedor;

-- Pedido 1 · listo para recoger · Bocagrande
INSERT INTO pedido
    (cliente_id, vendedor_id, estado, direccion_entrega, barrio, referencia,
     telefono_contacto, latitud, longitud, metodo_pago, total,
     costo_domicilio, notas)
SELECT @cliente, @vendedor, 'listo', 'Carrera 2 #11-41, Edificio Marbella',
       'Bocagrande', 'Torre azul, apto 502', '3012223344',
       10.40100, -75.55700, 'efectivo', 12000, 4000, '[demo] Sin ají, por favor'
WHERE @vendedor IS NOT NULL AND @cliente IS NOT NULL;
SET @p1 = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), 0);

-- Pedido 2 · listo para recoger · Manga
INSERT INTO pedido
    (cliente_id, vendedor_id, estado, direccion_entrega, barrio, referencia,
     telefono_contacto, latitud, longitud, metodo_pago, total,
     costo_domicilio, notas)
SELECT @cliente, @vendedor, 'listo', 'Avenida Jiménez #23-60',
       'Manga', 'Casa esquinera de rejas verdes', '3023334455',
       10.41440, -75.53300, 'transferencia', 8000, 3500, '[demo] Tocar el timbre dos veces'
WHERE @vendedor IS NOT NULL AND @cliente IS NOT NULL;
SET @p2 = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), 0);

-- Pedido 3 · aún preparándose · El Laguito
INSERT INTO pedido
    (cliente_id, vendedor_id, estado, direccion_entrega, barrio, referencia,
     telefono_contacto, latitud, longitud, metodo_pago, total,
     costo_domicilio, notas)
SELECT @cliente, @vendedor, 'preparando', 'Carrera 1 #4-120, Hotel Playa',
       'El Laguito', 'Preguntar en recepción', '3034445566',
       10.39500, -75.56000, 'tarjeta', 18000, 5000, '[demo]'
WHERE @vendedor IS NOT NULL AND @cliente IS NOT NULL;
SET @p3 = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), 0);

-- Pedido 4 · listo para recoger · Crespo (el más lejano)
INSERT INTO pedido
    (cliente_id, vendedor_id, estado, direccion_entrega, barrio, referencia,
     telefono_contacto, latitud, longitud, metodo_pago, total,
     costo_domicilio, notas)
SELECT @cliente, @vendedor, 'listo', 'Calle 70 #1-35',
       'Crespo', 'Frente al parque', '3045556677',
       10.44000, -75.51700, 'efectivo', 15000, 4500, '[demo] Llevar cambio de $50.000'
WHERE @vendedor IS NOT NULL AND @cliente IS NOT NULL;
SET @p4 = IF(ROW_COUNT() = 1, LAST_INSERT_ID(), 0);

-- Detalle de los pedidos de ejemplo
INSERT INTO pedido_detalle (pedido_id, nombre, cantidad, precio_unitario)
SELECT @p1, 'Empanadas de carne', 4, 2000 WHERE @p1 > 0
UNION ALL SELECT @p1, 'Carimañolas de queso', 2, 2000 WHERE @p1 > 0
UNION ALL SELECT @p2, 'Arepa de huevo', 2, 4000 WHERE @p2 > 0
UNION ALL SELECT @p3, 'Patacones con hogao', 3, 6000 WHERE @p3 > 0
UNION ALL SELECT @p4, 'Buñuelos', 5, 1500 WHERE @p4 > 0
UNION ALL SELECT @p4, 'Empanadas de queso', 4, 1875 WHERE @p4 > 0;
