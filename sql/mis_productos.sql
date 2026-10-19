-- ============================================================
-- mis_productos.sql  (usado por mis_productos.html)
-- Tablas de categorías y productos + consultas del panel del vendedor.
-- EJECUTAR SEGUNDO (después de registro.sql).
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS categoria (
  id     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(60)  NOT NULL,
  slug   VARCHAR(60)  NOT NULL,
  imagen VARCHAR(100) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categoria_slug (slug)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto (
  id           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  vendedor_id  INT UNSIGNED NOT NULL,
  categoria_id INT UNSIGNED NOT NULL,
  nombre       VARCHAR(120) NOT NULL,
  descripcion  VARCHAR(255) NULL,
  precio       INT UNSIGNED NOT NULL,              -- pesos colombianos, sin decimales
  imagen       VARCHAR(255) NULL,                  -- ej: uploads/abc123.jpg (NULL = imagen por defecto)
  etiqueta     VARCHAR(40)  NULL,                  -- "Más vendido", "Nuevo"...
  destacado    TINYINT(1)   NOT NULL DEFAULT 0,
  rating       DECIMAL(2,1) NOT NULL DEFAULT 0.0,
  resenas      INT UNSIGNED NOT NULL DEFAULT 0,
  ciudad       VARCHAR(80)  NOT NULL DEFAULT 'Cartagena, Bolívar',
  activo       TINYINT(1)   NOT NULL DEFAULT 1,    -- 0 = oculto para los clientes
  creado_en    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_producto_vendedor_nombre (vendedor_id, nombre),
  KEY ix_producto_categoria (categoria_id),
  CONSTRAINT fk_producto_vendedor
    FOREIGN KEY (vendedor_id)  REFERENCES usuario(id)   ON DELETE CASCADE,
  CONSTRAINT fk_producto_categoria
    FOREIGN KEY (categoria_id) REFERENCES categoria(id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Consultas que ejecuta app.py en el panel (referencia):
--
-- Ver MIS productos:
--   SELECT p.id, p.nombre, p.descripcion, p.precio, p.imagen,
--          p.activo, p.creado_en, c.nombre AS categoria
--   FROM producto p
--   JOIN categoria c ON c.id = p.categoria_id
--   WHERE p.vendedor_id = %s
--   ORDER BY p.creado_en DESC, p.id DESC;
--
-- Agregar un producto:
--   INSERT INTO producto (vendedor_id, categoria_id, nombre, descripcion, precio, imagen)
--   VALUES (%s, %s, %s, %s, %s, %s);
--
-- Ocultar / mostrar (solo si el producto es mío):
--   UPDATE producto SET activo = 1 - activo WHERE id = %s AND vendedor_id = %s;
--
-- Eliminar (solo si el producto es mío):
--   DELETE FROM producto WHERE id = %s AND vendedor_id = %s;
-- ------------------------------------------------------------
