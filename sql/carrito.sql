USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- SUPUESTO: usuario(id INT UNSIGNED), producto(id INT UNSIGNED), puesto(vendedor_id).
-- Seguro de ejecutar varias veces (MariaDB/XAMPP).

-- 1. Carrito guardado en la base de datos: uno por cliente, de UN solo puesto
CREATE TABLE IF NOT EXISTS carrito (
  usuario_id    INT UNSIGNED NOT NULL,
  vendedor_id   INT UNSIGNED NULL,
  actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id),
  CONSTRAINT fk_carrito_usuario
    FOREIGN KEY (usuario_id)  REFERENCES usuario(id) ON DELETE CASCADE,
  CONSTRAINT fk_carrito_puesto
    FOREIGN KEY (vendedor_id) REFERENCES puesto(vendedor_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 2. Productos dentro del carrito
CREATE TABLE IF NOT EXISTS carrito_item (
  usuario_id  INT UNSIGNED NOT NULL,
  producto_id INT UNSIGNED NOT NULL,
  cantidad    SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  agregado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, producto_id),
  CONSTRAINT fk_citem_carrito
    FOREIGN KEY (usuario_id)  REFERENCES carrito(usuario_id) ON DELETE CASCADE,
  CONSTRAINT fk_citem_producto
    FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE CASCADE,
  CONSTRAINT chk_citem_cantidad CHECK (cantidad BETWEEN 1 AND 99)
) ENGINE=InnoDB;

-- 3. Datos que necesita el pedido que sale del carrito
ALTER TABLE pedido
  ADD COLUMN IF NOT EXISTS vendedor_id  INT UNSIGNED NULL,
  ADD COLUMN IF NOT EXISTS tipo_entrega ENUM('recoger','domicilio') NOT NULL DEFAULT 'recoger',
  ADD COLUMN IF NOT EXISTS direccion    VARCHAR(200) NULL,
  ADD COLUMN IF NOT EXISTS notas        VARCHAR(255) NULL;

-- 4. Vista del carrito con precios reales (el precio sale SIEMPRE de producto)
CREATE OR REPLACE VIEW v_carrito AS
SELECT ci.usuario_id,
       c.vendedor_id,
       pr.id            AS producto_id,
       pr.nombre,
       pr.precio        AS precio_unitario,
       ci.cantidad,
       pr.precio * ci.cantidad AS subtotal,
       pr.imagen        AS img,
       (pr.activo = 1 AND pr.disponible = 1) AS disponible
FROM carrito_item ci
JOIN carrito  c  ON c.usuario_id = ci.usuario_id
JOIN producto pr ON pr.id = ci.producto_id;

-- 5. Agregar al carrito (úsalo desde Flask con %s; suma si ya existe).
--    Reemplaza @u = id del cliente, @p = id del producto.
--
--    INSERT INTO carrito (usuario_id, vendedor_id)
--    SELECT @u, pr.vendedor_id FROM producto pr WHERE pr.id = @p
--    ON DUPLICATE KEY UPDATE vendedor_id = vendedor_id;
--
--    INSERT INTO carrito_item (usuario_id, producto_id, cantidad)
--    VALUES (@u, @p, 1)
--    ON DUPLICATE KEY UPDATE cantidad = LEAST(cantidad + 1, 99);

-- 6. Comprobación
SELECT * FROM v_carrito;
