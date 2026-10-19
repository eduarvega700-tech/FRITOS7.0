-- ============================================================
-- registro.sql  (usado por registro.html y auth.html)
-- Crea la base de datos y la tabla de usuarios.
-- EJECUTAR PRIMERO.
-- ============================================================

CREATE DATABASE IF NOT EXISTS fritos_tech
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuario (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(120) NOT NULL,
  correo        VARCHAR(150) NOT NULL,
  clave_hash    VARCHAR(255) NOT NULL,          -- nunca se guarda la contraseña en texto plano
  rol           ENUM('cliente','vendedor','domiciliario','administrador')
                NOT NULL DEFAULT 'cliente',
  activo        TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso DATETIME     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_correo (correo)
) ENGINE=InnoDB;

-- Vendedores de ejemplo (los de data.py). Son "cuentas sin acceso":
-- su clave_hash no es válida, así que nadie puede iniciar sesión con ellas.
-- Sirven para que los productos de ejemplo tengan dueño.
INSERT IGNORE INTO usuario (nombre, correo, clave_hash, rol) VALUES
  ('La Delicia de la Abuela', 'delicia@fritostech.local',    'SIN-ACCESO', 'vendedor'),
  ('Sabor Caribe',            'saborcaribe@fritostech.local', 'SIN-ACCESO', 'vendedor'),
  ('El Sabor del Caribe',     'elsabor@fritostech.local',     'SIN-ACCESO', 'vendedor'),
  ('La Esquina del Sabor',    'esquina@fritostech.local',     'SIN-ACCESO', 'vendedor'),
  ('Doña Rosa Fritos',        'donarosa@fritostech.local',    'SIN-ACCESO', 'vendedor'),
  ('El Rincón Cartagenero',   'rincon@fritostech.local',      'SIN-ACCESO', 'vendedor'),
  ('La Matrona',              'matrona@fritostech.local',     'SIN-ACCESO', 'vendedor'),
  ('Fritos Don Luis',         'donluis@fritostech.local',     'SIN-ACCESO', 'vendedor'),
  ('Sazón Andino',            'sazonandino@fritostech.local', 'SIN-ACCESO', 'vendedor'),
  ('Mar y Sabor',             'marysabor@fritostech.local',   'SIN-ACCESO', 'vendedor');

-- ------------------------------------------------------------
-- Consulta que ejecuta app.py al registrar (referencia):
--   INSERT INTO usuario (nombre, correo, clave_hash, rol)
--   VALUES (%s, %s, %s, %s);
-- Si el correo ya existe, MySQL responde error 1062 (UNIQUE) y la
-- app muestra "Ese correo ya está registrado".
-- ------------------------------------------------------------
