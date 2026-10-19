-- ============================================================
-- auth.sql  (usado por auth.html)
-- Historial de inicios de sesión + consultas del login.
-- EJECUTAR QUINTO (último).
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS historial_acceso (
  id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id INT UNSIGNED NOT NULL,
  ip         VARCHAR(45)  NULL,
  fecha      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_acceso_usuario (usuario_id, fecha),
  CONSTRAINT fk_acceso_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Consultas que ejecuta app.py al iniciar sesión (referencia):
--
-- Buscar al usuario (el rol de la URL /acceso/<rol> debe coincidir):
--   SELECT id, nombre, correo, clave_hash, rol
--   FROM usuario
--   WHERE correo = %s AND rol = %s AND activo = 1;
--   → la contraseña se compara en Python con check_password_hash().
--
-- Si es correcta:
--   UPDATE usuario SET ultimo_acceso = NOW() WHERE id = %s;
--   INSERT INTO historial_acceso (usuario_id, ip) VALUES (%s, %s);
-- ------------------------------------------------------------
