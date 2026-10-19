-- ============================================================
-- explorar.sql  (usado por explorar.html e index.html)
-- Vista con los productos visibles para los clientes.
-- EJECUTAR CUARTO (después de index.sql).
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Los nombres de las columnas son los mismos que tenía data.py
-- (nombre, vendedor, categoria, precio, img...), por eso las plantillas
-- y el macro tarjeta_producto siguen funcionando igual.
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

-- ------------------------------------------------------------
-- Consultas que ejecuta app.py (referencia):
--
-- Explorar → "Todos":
--   SELECT * FROM v_productos_activos ORDER BY id;
--
-- Explorar → una categoría (ej. empanadas):
--   SELECT * FROM v_productos_activos WHERE categoria = %s ORDER BY id;
--
-- Chips de categorías:
--   SELECT nombre, slug, imagen FROM categoria ORDER BY id;
-- ------------------------------------------------------------
