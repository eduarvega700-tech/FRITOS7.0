USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 1. Disponibilidad de cada producto (1 = disponible, 0 = agotado)
ALTER TABLE producto
  ADD COLUMN disponible TINYINT(1) NOT NULL DEFAULT 1 AFTER activo;

-- 2. Un puesto por cada vendedor (la clave es el id del vendedor)
CREATE TABLE IF NOT EXISTS puesto (
  vendedor_id      INT UNSIGNED NOT NULL,
  nombre           VARCHAR(120) NOT NULL,
  descripcion      VARCHAR(255) NULL,
  direccion        VARCHAR(160) NULL,
  barrio           VARCHAR(80)  NULL,
  ciudad           VARCHAR(80)  NOT NULL DEFAULT 'Cartagena, Bolívar',
  horario          VARCHAR(80)  NULL,
  abierto          TINYINT(1)   NOT NULL DEFAULT 1,
  acepta_domicilio TINYINT(1)   NOT NULL DEFAULT 1,
  costo_domicilio  INT UNSIGNED NOT NULL DEFAULT 3000,
  PRIMARY KEY (vendedor_id),
  CONSTRAINT fk_puesto_vendedor
    FOREIGN KEY (vendedor_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Crear el puesto de los vendedores que ya existen
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT id, nombre FROM usuario WHERE rol = 'vendedor';