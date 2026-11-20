-- FRITOS TECH: ofertas y control de inventario por producto
-- Ejecutar una sola vez sobre la base de datos fritos_tech.
USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE producto
  ADD COLUMN cantidad_disponible INT UNSIGNED NOT NULL DEFAULT 0 AFTER disponible,
  ADD COLUMN oferta_activa TINYINT(1) NOT NULL DEFAULT 0 AFTER cantidad_disponible,
  ADD COLUMN descuento_porcentaje TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER oferta_activa;

-- Los productos existentes quedan con inventario 0 hasta que cada vendedor
-- registre la cantidad real desde "Editar producto". No inventamos existencias.
UPDATE producto SET disponible = (cantidad_disponible > 0);
