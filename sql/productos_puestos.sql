USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- SUPUESTO: producto(id, nombre, descripcion, precio, categoria_id, imagen,
--           activo, disponible, vendedor_id, creado_en) y categoria(id, nombre).
-- Es seguro ejecutarlo varias veces (MariaDB/XAMPP).

-- 1. Columnas necesarias para vender desde un puesto
ALTER TABLE producto
  ADD COLUMN IF NOT EXISTS disponible  TINYINT(1)   NOT NULL DEFAULT 1 AFTER activo,
  ADD COLUMN IF NOT EXISTS vendedor_id INT UNSIGNED NULL;

-- 2. Índice para listar rápido los productos de un puesto
ALTER TABLE producto ADD INDEX IF NOT EXISTS idx_producto_vendedor (vendedor_id, activo);

-- 3. Cada pedido queda ligado al puesto al que se le compró
ALTER TABLE pedido
  ADD COLUMN IF NOT EXISTS vendedor_id INT UNSIGNED NULL;

-- 4. Todo producto publicado debe tener su puesto (red de seguridad)
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT DISTINCT u.id, CONCAT('Puesto de ', u.nombre)
FROM producto pr JOIN usuario u ON u.id = pr.vendedor_id;

-- 5. Vista con los productos de cada puesto, lista para la página y el carrito.
--    En Flask:  SELECT * FROM v_producto_puesto WHERE puesto_id = %s
CREATE OR REPLACE VIEW v_producto_puesto AS
SELECT pr.id,
       pr.vendedor_id AS puesto_id,
       pr.nombre,
       pr.descripcion,
       pr.precio,
       c.nombre       AS categoria,
       pr.imagen      AS img,
       pr.imagen      AS imagen,
       pr.activo,
       pr.disponible
FROM producto pr
LEFT JOIN categoria c ON c.id = pr.categoria_id
WHERE pr.activo = 1;

-- 6. Comprobación: productos por puesto (debe salir tu puesto con su producto)
SELECT pu.vendedor_id, pu.nombre AS puesto, COUNT(v.id) AS productos
FROM puesto pu
LEFT JOIN v_producto_puesto v ON v.puesto_id = pu.vendedor_id
GROUP BY pu.vendedor_id, pu.nombre;
