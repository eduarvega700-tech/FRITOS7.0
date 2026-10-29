-- ============================================================
-- carrito_admin.sql  (usado por carrito.html y el panel admin)
-- Tablas de pedidos. EJECUTAR SEXTO (después de auth.sql).
-- Se puede ejecutar varias veces: no duplica nada.
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

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
