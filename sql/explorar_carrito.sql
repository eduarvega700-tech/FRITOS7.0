USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ═══════════════════════════════════════════════════════════════
-- Para que TODO producto de Explorar se pueda agregar al carrito.
-- La ruta /api/carrito/agregar solo acepta un producto si:
--   · producto.activo = 1 y producto.disponible = 1
--   · producto.vendedor_id apunta a un usuario que tenga fila en puesto
--   · ese puesto tiene abierto = 1
-- Si algo de eso falla, el botón no agrega. Este archivo lo corrige.
-- SUPUESTO: producto.vendedor_id es el dueño del producto.
-- Se puede ejecutar varias veces (MariaDB/XAMPP).
-- ═══════════════════════════════════════════════════════════════

-- 0. DIAGNÓSTICO: productos que hoy NO se pueden agregar y por qué
SELECT pr.id, pr.nombre, pr.activo, pr.disponible, pr.vendedor_id,
       pu.abierto,
       CASE
         WHEN pr.vendedor_id IS NULL        THEN 'sin vendedor_id'
         WHEN pu.vendedor_id IS NULL        THEN 'su vendedor no tiene puesto'
         WHEN pu.abierto = 0                THEN 'puesto cerrado'
         WHEN pr.activo = 0                 THEN 'oculto'
         WHEN pr.disponible = 0             THEN 'agotado'
         ELSE 'OK'
       END AS motivo
FROM producto pr
LEFT JOIN puesto pu ON pu.vendedor_id = pr.vendedor_id
ORDER BY motivo, pr.id;

-- 1. Columnas necesarias (no hace nada si ya existen)
ALTER TABLE producto
  ADD COLUMN IF NOT EXISTS disponible  TINYINT(1)   NOT NULL DEFAULT 1 AFTER activo,
  ADD COLUMN IF NOT EXISTS vendedor_id INT UNSIGNED NULL;

-- 2. Productos que quedaron "agotados" por defecto o sin valor: dejarlos disponibles
UPDATE producto SET disponible = 1 WHERE disponible IS NULL OR disponible = 0;

-- 3. Productos sin dueño: asignarlos a un vendedor.
--    CAMBIA 'el mono' por el nombre de la cuenta vendedora que será dueña
--    de los productos de catálogo (o pon directamente su id).
SET @dueno = (SELECT id FROM usuario WHERE nombre LIKE '%el mono%' LIMIT 1);
UPDATE producto SET vendedor_id = @dueno
WHERE vendedor_id IS NULL AND @dueno IS NOT NULL;

-- 4. Todo vendedor_id que tenga productos debe tener su puesto
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT DISTINCT u.id, CONCAT('Puesto de ', u.nombre)
FROM producto pr JOIN usuario u ON u.id = pr.vendedor_id;

-- 5. Abrir los puestos para poder comprar (quita esta línea si quieres
--    conservar algún puesto cerrado)
UPDATE puesto SET abierto = 1;

-- 6. Las tablas del carrito deben existir (de carrito.sql)
CREATE TABLE IF NOT EXISTS carrito (
  usuario_id     INT UNSIGNED NOT NULL,
  vendedor_id    INT UNSIGNED NULL,
  actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id),
  CONSTRAINT fk_carrito_usuario FOREIGN KEY (usuario_id)  REFERENCES usuario(id) ON DELETE CASCADE,
  CONSTRAINT fk_carrito_puesto  FOREIGN KEY (vendedor_id) REFERENCES puesto(vendedor_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS carrito_item (
  usuario_id  INT UNSIGNED NOT NULL,
  producto_id INT UNSIGNED NOT NULL,
  cantidad    SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  agregado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, producto_id),
  CONSTRAINT fk_citem_carrito  FOREIGN KEY (usuario_id)  REFERENCES carrito(usuario_id) ON DELETE CASCADE,
  CONSTRAINT fk_citem_producto FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. COMPROBACIÓN: ahora todos deben decir OK
SELECT pr.id, pr.nombre,
       IF(pr.activo = 1 AND pr.disponible = 1 AND pu.abierto = 1, 'OK', 'REVISAR') AS estado
FROM producto pr
LEFT JOIN puesto pu ON pu.vendedor_id = pr.vendedor_id
ORDER BY estado DESC, pr.id;
