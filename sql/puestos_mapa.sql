USE fritos_tech;

-- 1. Agrega latitud y longitud solo si todavía no existen
SET @existe := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'puesto' AND COLUMN_NAME = 'latitud'
);
SET @sentencia := IF(@existe = 0,
  'ALTER TABLE puesto
     ADD COLUMN latitud  DECIMAL(9,6) NULL AFTER ciudad,
     ADD COLUMN longitud DECIMAL(9,6) NULL AFTER latitud',
  'SELECT 1');
PREPARE s FROM @sentencia;
EXECUTE s;
DEALLOCATE PREPARE s;

-- 2. Coordenadas APROXIMADAS de ejemplo para los 10 vendedores de prueba
UPDATE puesto pu
JOIN usuario u ON u.id = pu.vendedor_id
JOIN (
  SELECT 'delicia@fritostech.local' AS correo, 'Centro Histórico' AS barrio, 10.424200 AS lat, -75.551300 AS lng
  UNION ALL SELECT 'saborcaribe@fritostech.local', 'Getsemaní',      10.422000, -75.546000
  UNION ALL SELECT 'elsabor@fritostech.local',     'Bocagrande',     10.401000, -75.557000
  UNION ALL SELECT 'esquina@fritostech.local',     'Manga',          10.413500, -75.536000
  UNION ALL SELECT 'donarosa@fritostech.local',    'Pie de la Popa', 10.418000, -75.523000
  UNION ALL SELECT 'rincon@fritostech.local',      'Torices',        10.418000, -75.527000
  UNION ALL SELECT 'matrona@fritostech.local',     'Crespo',         10.444000, -75.514000
  UNION ALL SELECT 'donluis@fritostech.local',     'El Bosque',      10.398000, -75.501000
  UNION ALL SELECT 'sazonandino@fritostech.local', 'Los Alpes',      10.380000, -75.470000
  UNION ALL SELECT 'marysabor@fritostech.local',   'Bazurto',        10.408000, -75.516000
) t ON t.correo = u.correo
SET pu.barrio = t.barrio,
    pu.latitud = t.lat,
    pu.longitud = t.lng
WHERE pu.latitud IS NULL;