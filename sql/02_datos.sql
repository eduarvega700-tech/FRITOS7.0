-- ============================================================
-- 02_datos.sql   ·   FRITOS TECH
-- SOLO DATOS DE EJEMPLO: vendedores, categorías, 38 productos
-- (con su descripción), puestos y coordenadas del mapa.
--
-- EJECUTAR SEGUNDO (después de 01_estructura.sql).
-- Se puede ejecutar varias veces: no duplica datos
-- (INSERT IGNORE) y no toca a los usuarios reales.
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- MySQL Workbench bloquea los UPDATE sin clave primaria; se apaga mientras corre este archivo
SET SQL_SAFE_UPDATES = 0;


-- ------------------------------------------------------------
-- 1. VENDEDORES DE EJEMPLO
-- Son "cuentas sin acceso": su clave_hash no es válida, así que nadie
-- puede iniciar sesión con ellas. Sirven para que los productos tengan dueño.
-- ------------------------------------------------------------
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
-- 2. UN PUESTO POR CADA VENDEDOR
-- ------------------------------------------------------------
INSERT IGNORE INTO puesto (vendedor_id, nombre)
SELECT id, nombre FROM usuario WHERE rol = 'vendedor';


-- ------------------------------------------------------------
-- 3. CATEGORÍAS
-- ------------------------------------------------------------
INSERT IGNORE INTO categoria (nombre, slug, imagen) VALUES
  ('Empanadas',       'empanadas',       'empanadas.png'),
  ('Arepas de huevo', 'arepas-de-huevo', 'arepas.png'),
  ('Carimañolas',     'carimañola',      'carimañola.png'),
  ('Patacones',       'patacones',       'patacones.png'),
  ('Buñuelos',        'buñuelos',        'buñuelos.png'),
  ('Otros',           'otros',           'otros.png');


-- ------------------------------------------------------------
-- 4. LOS 38 PRODUCTOS (ya incluyen su descripción)
-- Entran con 0 unidades; el paso 6 les pone existencias de prueba.
-- ------------------------------------------------------------
INSERT IGNORE INTO producto
  (vendedor_id, categoria_id, nombre, descripcion, precio, etiqueta, destacado, rating, resenas)
SELECT u.id, c.id, t.nombre, t.descripcion, t.precio, t.etiqueta, t.destacado, t.rating, t.resenas
FROM (
  SELECT 'delicia@fritostech.local' AS correo, 'empanadas' AS slug, 'Empanadas de carne' AS nombre, CAST('Empanadas crujientes de maíz rellenas de carne molida bien sazonada.' AS CHAR(255)) AS descripcion, 2000 AS precio, CAST('Más vendido' AS CHAR(40)) AS etiqueta, 1 AS destacado, 4.8 AS rating, 124 AS resenas
  UNION ALL SELECT 'saborcaribe@fritostech.local','arepas-de-huevo','Arepa de huevo','Arepa de maíz frita con un huevo entero en el centro, el clásico de la costa.',3000,'Nuevo',1,4.9,98
  UNION ALL SELECT 'elsabor@fritostech.local','carimañola','Carimañolas de yuca','Masa de yuca en forma de torpedo, rellena de carne y frita hasta dorar.',2500,'Más vendido',1,4.7,76
  UNION ALL SELECT 'esquina@fritostech.local','patacones','Patacones con hogao','Plátano verde frito y aplastado, acompañado de hogao casero de tomate y cebolla.',3500,'Popular',1,4.8,110
  UNION ALL SELECT 'donarosa@fritostech.local','buñuelos','Buñuelos','Bolitas de masa fritas, doradas por fuera y suaves por dentro.',1500,NULL,0,4.6,52
  UNION ALL SELECT 'rincon@fritostech.local','empanadas','Empanada de pollo','Empanada dorada rellena de pollo desmechado con un toque criollo.',2000,NULL,0,4.7,88
  UNION ALL SELECT 'matrona@fritostech.local','arepas-de-huevo','Arepa de huevo especial','Arepa de huevo con relleno extra, más grande y llena de sabor.',3500,NULL,0,4.8,64
  UNION ALL SELECT 'donluis@fritostech.local','patacones','Patacón con queso','Patacón crocante cubierto con queso costeño rallado.',3000,NULL,0,4.5,41
  UNION ALL SELECT 'delicia@fritostech.local','empanadas','Empanadas de queso','Masa de maíz crujiente rellena de queso costeño derretido.',2000,NULL,0,4.7,58
  UNION ALL SELECT 'sazonandino@fritostech.local','empanadas','Empanadas de pipián','Empanadas de papa y maní al estilo de Nariño, servidas con ají.',2000,NULL,0,4.6,33
  UNION ALL SELECT 'rincon@fritostech.local','empanadas','Empanadas vallecaucanas','Pequeñas empanadas de masa de maíz rellenas de carne y papa.',2000,NULL,0,4.5,29
  UNION ALL SELECT 'donluis@fritostech.local','empanadas','Empanadas de cambray','Empanadas de masa de trigo, doradas y rellenas de carne o queso.',2000,NULL,0,4.6,47
  UNION ALL SELECT 'saborcaribe@fritostech.local','empanadas','Empanadas de yuca','Masa suave de yuca frita, rellena de queso o carne.',2000,NULL,0,4.7,52
  UNION ALL SELECT 'marysabor@fritostech.local','empanadas','Empanadas de camarón','Empanadas crocantes rellenas de camarones guisados, típicas del Caribe.',3000,NULL,0,4.8,61
  UNION ALL SELECT 'matrona@fritostech.local','arepas-de-huevo','Arepa de huevo con carne','Arepa frita con huevo en el centro y relleno generoso de carne molida.',3000,NULL,0,4.8,73
  UNION ALL SELECT 'saborcaribe@fritostech.local','arepas-de-huevo','Arepa de huevo con queso','Arepa de huevo crujiente con mucho queso costeño derretido por dentro.',3000,NULL,0,4.7,55
  UNION ALL SELECT 'elsabor@fritostech.local','carimañola','Carimañolas de queso','Masa de yuca frita rellena de queso suave que se derrite al morder.',2000,NULL,0,4.7,44
  UNION ALL SELECT 'esquina@fritostech.local','patacones','Patacón pisao','Plátano verde aplastado y frito dos veces, crocante y con sal justa.',3000,NULL,0,4.8,69
  UNION ALL SELECT 'donarosa@fritostech.local','buñuelos','Buñuelos de frijol','Buñuelos del Caribe hechos con frijol cabecita negra, dorados y sabrosos.',1500,NULL,0,4.6,38
  UNION ALL SELECT 'rincon@fritostech.local','otros','Papa rellena','Bola de papa rellena de carne guisada, frita hasta quedar dorada.',2000,NULL,0,4.7,60
  UNION ALL SELECT 'donluis@fritostech.local','otros','Deditos de queso','Bastones de masa rellenos de queso que se derrite al morderlos.',1500,NULL,0,4.5,36
  UNION ALL SELECT 'delicia@fritostech.local','otros','Marranitas','Plátano maduro frito relleno de chicharrón, dulce y salado a la vez.',1500,NULL,0,4.6,42
  UNION ALL SELECT 'sazonandino@fritostech.local','otros','Aborrajados','Plátano maduro con queso, apanado y frito hasta quedar crujiente.',2000,NULL,0,4.8,57
  UNION ALL SELECT 'saborcaribe@fritostech.local','otros','Quibbes','Croquetas de trigo y carne con especias, herencia árabe del Caribe.',2000,NULL,0,4.7,49
  UNION ALL SELECT 'rincon@fritostech.local','otros','Pastel de pollo','Pastel hojaldrado y dorado relleno de pollo guisado con verduras.',2000,NULL,0,4.6,35
  UNION ALL SELECT 'donarosa@fritostech.local','otros','Yuca frita','Bastones de yuca fritos, crujientes por fuera y suaves por dentro.',1500,NULL,0,4.5,31
  UNION ALL SELECT 'esquina@fritostech.local','otros','Tajadas de plátano maduro','Rodajas de plátano maduro fritas, caramelizadas y dulces.',1500,NULL,0,4.6,40
  UNION ALL SELECT 'donluis@fritostech.local','otros','Papas criollas fritas','Papitas criollas amarillas fritas enteras, doradas y con sal.',1500,NULL,0,4.5,28
  UNION ALL SELECT 'matrona@fritostech.local','otros','Chicharrón','Trozos de cerdo fritos, bien crocantes por fuera y jugosos por dentro.',3000,NULL,0,4.8,66
  UNION ALL SELECT 'elsabor@fritostech.local','otros','Pasteles de yuca','Pasteles de masa de yuca rellenos de carne o queso, fritos al momento.',2000,NULL,0,4.6,37
  UNION ALL SELECT 'saborcaribe@fritostech.local','otros','Arepa frita','Arepa de maíz frita, inflada y dorada, perfecta para acompañar.',1500,NULL,0,4.5,30
  UNION ALL SELECT 'sazonandino@fritostech.local','otros','Hojaldras','Masa de trigo frita, aireada y ligera, ideal para el desayuno.',1500,NULL,0,4.6,34
  UNION ALL SELECT 'donarosa@fritostech.local','otros','Bolitas de yuca con queso','Bolitas de yuca rellenas de queso, crujientes y bien suaves por dentro.',1500,NULL,0,4.7,46
  UNION ALL SELECT 'matrona@fritostech.local','otros','Arepa de choclo frita','Arepa de maíz tierno frita, ligeramente dulce y con queso.',3000,NULL,0,4.7,43
  UNION ALL SELECT 'marysabor@fritostech.local','otros','Cazón frito','Trozos de cazón apanados y fritos, frescos del mar Caribe.',3000,NULL,0,4.6,32
  UNION ALL SELECT 'esquina@fritostech.local','otros','Plátano relleno frito','Plátano frito relleno de carne o queso, dulce por fuera y sabroso por dentro.',3000,NULL,0,4.7,39
  UNION ALL SELECT 'donluis@fritostech.local','otros','Tostadas de plátano verde','Láminas finas de plátano verde fritas, crocantes y saladas.',1500,NULL,0,4.5,27
  UNION ALL SELECT 'rincon@fritostech.local','otros','Papa rellena con arroz y huevo','Papa rellena con carne, arroz y huevo cocido, una versión más contundente.',3000,NULL,0,4.8,51
) AS t
JOIN usuario   u ON u.correo = t.correo
JOIN categoria c ON c.slug   = t.slug;


-- ------------------------------------------------------------
-- 5. UBICACIÓN DE LOS PUESTOS EN EL MAPA (coordenadas aproximadas de ejemplo)
-- ------------------------------------------------------------
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


-- ------------------------------------------------------------
-- 6. EXISTENCIAS DE PRUEBA para los productos de ejemplo
--    (para que no salgan todos "Agotado"). Solo toca los productos de
--    los vendedores @fritostech.local que estén en 0 unidades.
--    Si no las quieres, borra este bloque o cambia el 20.
-- ------------------------------------------------------------
UPDATE producto p
JOIN usuario u ON u.id = p.vendedor_id
SET p.cantidad_disponible = 20,
    p.disponible = 1
WHERE u.correo LIKE '%@fritostech.local'
  AND p.cantidad_disponible = 0;

SET SQL_SAFE_UPDATES = 1;


-- ------------------------------------------------------------
-- Comprobaciones (quita los "--" para ejecutarlas):
-- SELECT COUNT(*) FROM usuario WHERE rol = 'vendedor';      -- 10
-- SELECT COUNT(*) FROM categoria;                           -- 6
-- SELECT COUNT(*) FROM producto;                            -- 38
-- SELECT COUNT(*) FROM puesto WHERE latitud IS NOT NULL;    -- 10
-- SELECT id, nombre FROM producto WHERE descripcion IS NULL OR descripcion = '';  -- 0 filas
-- ------------------------------------------------------------
