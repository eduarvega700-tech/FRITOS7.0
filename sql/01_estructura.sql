-- ============================================================
-- 01_estructura.sql   ·   FRITOS TECH
-- SOLO ESTRUCTURA: base de datos, tablas y v ista. No trae datos.
--
-- EJECUTAR PRIMERO (y luego 02_datos.sql).
-- Se puede ejecutar varias veces sin borrar nada:
--   · Si la tabla ya existe, no la toca.
--   · Si a una tabla vieja le faltan columnas (cantidad_disponible,
--     oferta_activa, descuento_porcentaje, latitud...), las agrega.
-- ============================================================

CREATE DATABASE IF NOT EXISTS fritos_tech
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 1. USUARIOS (clientes, vendedores, domiciliarios, administrador)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(120) NOT NULL,
  correo        VARCHAR(150) NOT NULL,
  clave_hash    VARCHAR(255) NOT NULL,          -- nunca se guarda la contraseña en texto plano
  rol           ENUM('cliente','vendedor','domiciliario','administrador')
                NOT NULL DEFAULT 'cliente',
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso DATETIME     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_correo (correo)
) ENGINE=InnoDB;

-- Historial de inicios de sesión
CREATE TABLE IF NOT EXISTS historial_acceso (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id INT UNSIGNED NOT NULL,
  ip         VARCHAR(45)  NULL,
  fecha      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_acceso_usuario (usuario_id, fecha),
  CONSTRAINT fk_acceso_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ------------------------------------------------------------
-- 2. CATEGORÍAS Y PRODUCTOS (con inventario y ofertas)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categoria (
  id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(60)  NOT NULL,
  slug   VARCHAR(60)  NOT NULL,
  imagen VARCHAR(100) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categoria_slug (slug)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto (
  id                   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  vendedor_id          INT UNSIGNED NOT NULL,
  categoria_id         INT UNSIGNED NOT NULL,
  nombre               VARCHAR(120) NOT NULL,
  descripcion          VARCHAR(255) NULL,
  precio               INT UNSIGNED NOT NULL,              -- pesos colombianos, sin decimales
  imagen               VARCHAR(255) NULL,                  -- ej: uploads/abc123.jpg
  etiqueta             VARCHAR(40)  NULL,                  -- "Más vendido", "Nuevo"...
  destacado            TINYINT(1)   NOT NULL DEFAULT 0,
  rating               DECIMAL(2,1) NOT NULL DEFAULT 0.0,
  resenas              INT UNSIGNED NOT NULL DEFAULT 0,
  ciudad               VARCHAR(80)  NOT NULL DEFAULT 'Cartagena, Bolívar',
  activo               TINYINT(1)   NOT NULL DEFAULT 1,    -- 0 = oculto para los clientes
  disponible           TINYINT(1)   NOT NULL DEFAULT 1,    -- 1 = disponible, 0 = agotado
  cantidad_disponible  INT UNSIGNED NOT NULL DEFAULT 0,    -- unidades en inventario
  oferta_activa        TINYINT(1)   NOT NULL DEFAULT 0,    -- 1 = tiene descuento
  descuento_porcentaje TINYINT UNSIGNED NOT NULL DEFAULT 0, -- ej: 20 = 20 %
  creado_en            DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_producto_vendedor_nombre (vendedor_id, nombre),
  KEY ix_producto_categoria (categoria_id),
  CONSTRAINT fk_producto_vendedor
    FOREIGN KEY (vendedor_id)  REFERENCES usuario(id)   ON DELETE CASCADE,
  CONSTRAINT fk_producto_categoria
    FOREIGN KEY (categoria_id) REFERENCES categoria(id)
) ENGINE=InnoDB;


-- ------------------------------------------------------------
-- 3. PUESTOS (uno por vendedor, con ubicación para el mapa)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS puesto (
  vendedor_id      INT UNSIGNED NOT NULL,
  nombre           VARCHAR(120) NOT NULL,
  descripcion      VARCHAR(255) NULL,
  direccion        VARCHAR(160) NULL,
  barrio           VARCHAR(80)  NULL,
  ciudad           VARCHAR(80)  NOT NULL DEFAULT 'Cartagena, Bolívar',
  latitud          DECIMAL(9,6) NULL,
  longitud         DECIMAL(9,6) NULL,
  horario          VARCHAR(80)  NULL,
  abierto          TINYINT(1)   NOT NULL DEFAULT 1,
  acepta_domicilio TINYINT(1)   NOT NULL DEFAULT 1,
  costo_domicilio  INT UNSIGNED NOT NULL DEFAULT 3000,
  PRIMARY KEY (vendedor_id),
  CONSTRAINT fk_puesto_vendedor
    FOREIGN KEY (vendedor_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ------------------------------------------------------------
-- 4. PEDIDOS (carrito y compras)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  cliente_id   INT UNSIGNED NOT NULL,
  tipo_entrega ENUM('recoger','domicilio') NOT NULL DEFAULT 'recoger',
  direccion    VARCHAR(200) NULL,                  -- solo si es domicilio
  notas        VARCHAR(255) NULL,
  total        INT UNSIGNED NOT NULL,              -- pesos colombianos
  estado       ENUM('pendiente','preparando','listo','entregado','cancelado')
               NOT NULL DEFAULT 'pendiente',
  creado_en    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_pedido_cliente (cliente_id, creado_en),
  KEY ix_pedido_estado (estado),
  CONSTRAINT fk_pedido_cliente
    FOREIGN KEY (cliente_id) REFERENCES usuario(id)
) ENGINE=InnoDB;

-- Se guarda el nombre y el precio de cada ítem en el momento de la compra:
-- si el vendedor cambia o borra el producto, el pedido no se altera.
CREATE TABLE IF NOT EXISTS pedido_item (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  pedido_id       INT UNSIGNED NOT NULL,
  producto_id     INT UNSIGNED NULL,
  nombre          VARCHAR(120) NOT NULL,
  precio_unitario INT UNSIGNED NOT NULL,
  cantidad        INT UNSIGNED NOT NULL,
  PRIMARY KEY (id),
  KEY ix_item_pedido (pedido_id),
  CONSTRAINT fk_item_pedido
    FOREIGN KEY (pedido_id)   REFERENCES pedido(id)   ON DELETE CASCADE,
  CONSTRAINT fk_item_producto
    FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE SET NULL
) ENGINE=InnoDB;


-- ------------------------------------------------------------
-- 5. COLUMNAS QUE PUEDEN FALTAR EN UNA BASE DE DATOS ANTIGUA
--    (si la base es nueva, no hace nada: ya vienen en el CREATE TABLE)
-- ------------------------------------------------------------
SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'producto' AND COLUMN_NAME = 'disponible') = 0,
  'ALTER TABLE producto ADD COLUMN disponible TINYINT(1) NOT NULL DEFAULT 1 AFTER activo',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'producto' AND COLUMN_NAME = 'cantidad_disponible') = 0,
  'ALTER TABLE producto ADD COLUMN cantidad_disponible INT UNSIGNED NOT NULL DEFAULT 0 AFTER disponible',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'producto' AND COLUMN_NAME = 'oferta_activa') = 0,
  'ALTER TABLE producto ADD COLUMN oferta_activa TINYINT(1) NOT NULL DEFAULT 0 AFTER cantidad_disponible',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'producto' AND COLUMN_NAME = 'descuento_porcentaje') = 0,
  'ALTER TABLE producto ADD COLUMN descuento_porcentaje TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER oferta_activa',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'puesto' AND COLUMN_NAME = 'latitud') = 0,
  'ALTER TABLE puesto ADD COLUMN latitud DECIMAL(9,6) NULL AFTER ciudad',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

SET @sql := IF(
  (SELECT COUNT(*) FROM information_schema.COLUMNS
   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'puesto' AND COLUMN_NAME = 'longitud') = 0,
  'ALTER TABLE puesto ADD COLUMN longitud DECIMAL(9,6) NULL AFTER latitud',
  'SELECT 1');
PREPARE s FROM @sql; EXECUTE s; DEALLOCATE PREPARE s;

-- Deja "disponible" coherente con las existencias (0 unidades = agotado)
SET SQL_SAFE_UPDATES = 0;
UPDATE producto SET disponible = (cantidad_disponible > 0);
SET SQL_SAFE_UPDATES = 1;


-- ------------------------------------------------------------
-- 6. VISTA: productos visibles para los clientes (index y explorar)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW v_productos_activos AS
SELECT
  p.id,
  p.nombre,
  p.vendedor_id,
  u.nombre                AS vendedor,
  p.rating,
  p.resenas,
  p.ciudad,
  p.precio,
  p.etiqueta,
  p.destacado,
  c.slug                  AS categoria,
  c.nombre                AS categoria_nombre,
  p.descripcion,
  ''                      AS emoji,
  COALESCE(p.imagen, '')  AS img
FROM producto p
JOIN usuario   u ON u.id = p.vendedor_id
JOIN categoria c ON c.id = p.categoria_id
WHERE p.activo = 1
  AND u.activo = 1;

-- Comprobación: debe listar las 8 tablas y la vista
-- SHOW FULL TABLES;
