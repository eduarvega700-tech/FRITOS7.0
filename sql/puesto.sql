USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 1. Disponibilidad de cada producto (1 = disponible, 0 = agotado)
--    (IF NOT EXISTS: funciona en MariaDB/XAMPP y no falla si ya la agregaste)
ALTER TABLE producto
  ADD COLUMN IF NOT EXISTS disponible TINYINT(1) NOT NULL DEFAULT 1 AFTER activo;

-- 2. Un puesto por cada vendedor (la clave es el id del vendedor)
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

-- 3. Crear el puesto de los vendedores que ya existen (no toca los que ya tienen)
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT id, CONCAT('Puesto de ', nombre) FROM usuario WHERE rol = 'vendedor';

-- 4. Crear también el puesto de quien ya publicó productos, aunque su rol sea otro
--    SUPUESTO: producto.vendedor_id es el dueño del producto.
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT DISTINCT u.id, CONCAT('Puesto de ', u.nombre)
FROM producto pr JOIN usuario u ON u.id = pr.vendedor_id;

-- 5. AUTOMÁTICO: cada cuenta nueva (o que pase a vendedor) recibe su puesto
DROP TRIGGER IF EXISTS trg_usuario_vendedor_ins;
DROP TRIGGER IF EXISTS trg_usuario_vendedor_upd;
DROP TRIGGER IF EXISTS trg_producto_crea_puesto;

DELIMITER //
CREATE TRIGGER trg_usuario_vendedor_ins AFTER INSERT ON usuario
FOR EACH ROW
BEGIN
    IF NEW.rol = 'vendedor' THEN
        INSERT IGNORE INTO puesto (vendedor_id, nombre)
        VALUES (NEW.id, CONCAT('Puesto de ', NEW.nombre));
    END IF;
END//

CREATE TRIGGER trg_usuario_vendedor_upd AFTER UPDATE ON usuario
FOR EACH ROW
BEGIN
    IF NEW.rol = 'vendedor' AND OLD.rol <> 'vendedor' THEN
        INSERT IGNORE INTO puesto (vendedor_id, nombre)
        VALUES (NEW.id, CONCAT('Puesto de ', NEW.nombre));
    END IF;
END//

-- Red de seguridad: al publicar un producto, si esa cuenta no tiene puesto, se crea
CREATE TRIGGER trg_producto_crea_puesto AFTER INSERT ON producto
FOR EACH ROW
BEGIN
    INSERT IGNORE INTO puesto (vendedor_id, nombre)
    SELECT u.id, CONCAT('Puesto de ', u.nombre)
    FROM usuario u WHERE u.id = NEW.vendedor_id;
END//
DELIMITER ;
