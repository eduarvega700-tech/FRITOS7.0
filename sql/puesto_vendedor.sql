-- FRITOS TECH · Puesto automático para cada vendedor
-- Tabla: puesto (PK = vendedor_id, que es el id del usuario vendedor)
-- SUPUESTO: usuario(id, nombre, rol) y el rol de vendedor es 'vendedor'.
-- Verifica antes con:  SELECT id, nombre, rol FROM usuario;

-- 1) Crear el puesto de cada vendedor que todavía no tenga
INSERT INTO puesto (vendedor_id, nombre, ciudad, abierto, acepta_domicilio, costo_domicilio)
SELECT u.id, CONCAT('Puesto de ', u.nombre), 'Turbaco, Bolívar', 1, 1, 3000
FROM usuario u
WHERE u.rol = 'vendedor'
  AND NOT EXISTS (SELECT 1 FROM puesto p WHERE p.vendedor_id = u.id);

-- 2) Automático: al registrar un usuario vendedor se crea su puesto
DROP TRIGGER IF EXISTS trg_usuario_vendedor_ins;
DROP TRIGGER IF EXISTS trg_usuario_vendedor_upd;

DELIMITER //
CREATE TRIGGER trg_usuario_vendedor_ins AFTER INSERT ON usuario
FOR EACH ROW
BEGIN
    IF NEW.rol = 'vendedor' THEN
        INSERT IGNORE INTO puesto (vendedor_id, nombre, ciudad, abierto, acepta_domicilio, costo_domicilio)
        VALUES (NEW.id, CONCAT('Puesto de ', NEW.nombre), 'Turbaco, Bolívar', 1, 1, 3000);
    END IF;
END//

CREATE TRIGGER trg_usuario_vendedor_upd AFTER UPDATE ON usuario
FOR EACH ROW
BEGIN
    IF NEW.rol = 'vendedor' AND OLD.rol <> 'vendedor' THEN
        INSERT IGNORE INTO puesto (vendedor_id, nombre, ciudad, abierto, acepta_domicilio, costo_domicilio)
        VALUES (NEW.id, CONCAT('Puesto de ', NEW.nombre), 'Turbaco, Bolívar', 1, 1, 3000);
    END IF;
END//
DELIMITER ;

-- 3) (Opcional) Personaliza TU puesto. Cambia 1 por tu id de usuario.
UPDATE puesto
SET nombre = 'Mi local de fritos',
    descripcion = 'Fritos recién hechos todos los días',
    barrio = 'Centro',
    direccion = 'Calle 1 # 2-3',
    horario = 'Lun-Sáb 4:00 pm - 10:00 pm'
WHERE vendedor_id = 1;
