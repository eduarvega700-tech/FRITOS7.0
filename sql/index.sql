-- ============================================================
-- index.sql  (usado por index.html)
-- Carga las categorías y los 38 productos que estaban en data.py.
-- EJECUTAR TERCERO (después de registro.sql y mis_productos.sql).
-- Se puede ejecutar varias veces: no duplica datos.
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT IGNORE INTO categoria (nombre, slug, imagen) VALUES
  ('Empanadas',       'empanadas',       'empanadas.png'),
  ('Arepas de huevo', 'arepas-de-huevo', 'arepas.png'),
  ('Carimañolas',     'carimañola',      'carimañola.png'),
  ('Patacones',       'patacones',       'patacones.png'),
  ('Buñuelos',        'buñuelos',        'buñuelos.png'),
  ('Otros',           'otros',           'otros.png');

INSERT IGNORE INTO producto
  (vendedor_id, categoria_id, nombre, descripcion, precio, etiqueta, destacado, rating, resenas)
SELECT u.id, c.id, t.nombre, t.descripcion, t.precio, t.etiqueta, t.destacado, t.rating, t.resenas
FROM (
  SELECT 'delicia@fritostech.local' AS correo, 'empanadas' AS slug, 'Empanadas de carne' AS nombre, CAST(NULL AS CHAR(255)) AS descripcion, 2000 AS precio, CAST('Más vendido' AS CHAR(40)) AS etiqueta, 1 AS destacado, 4.8 AS rating, 124 AS resenas
  UNION ALL SELECT 'saborcaribe@fritostech.local','arepas-de-huevo','Arepa de huevo',NULL,3000,'Nuevo',1,4.9,98
  UNION ALL SELECT 'elsabor@fritostech.local','carimañola','Carimañolas de yuca',NULL,2500,'Más vendido',1,4.7,76
  UNION ALL SELECT 'esquina@fritostech.local','patacones','Patacones con hogao',NULL,3500,'Popular',1,4.8,110
  UNION ALL SELECT 'donarosa@fritostech.local','buñuelos','Buñuelos',NULL,1500,NULL,0,4.6,52
  UNION ALL SELECT 'rincon@fritostech.local','empanadas','Empanada de pollo',NULL,2000,NULL,0,4.7,88
  UNION ALL SELECT 'matrona@fritostech.local','arepas-de-huevo','Arepa de huevo especial',NULL,3500,NULL,0,4.8,64
  UNION ALL SELECT 'donluis@fritostech.local','patacones','Patacón con queso',NULL,3000,NULL,0,4.5,41
  UNION ALL SELECT 'delicia@fritostech.local','empanadas','Empanadas de queso','Masa de maíz crujiente rellena de queso costeño derretido.',2000,NULL,0,4.7,58
  UNION ALL SELECT 'sazonandino@fritostech.local','empanadas','Empanadas de pipián','Empanadas de papa y maní al estilo de Nariño, servidas con ají.',2000,NULL,0,4.6,33
  UNION ALL SELECT 'rincon@fritostech.local','empanadas','Empanadas vallecaucanas','Pequeñas empanadas de masa de maíz rellenas de carne y papa.',2000,NULL,0,4.5,29
  UNION ALL SELECT 'donluis@fritostech.local','empanadas','Empanadas de cambray','Empanadas de masa de trigo, doradas y rellenas de carne o queso.',2000,NULL,0,4.6,47
  UNION ALL SELECT 'saborcaribe@fritostech.local','empanadas','Empanadas de yuca','Masa suave de yuca frita, rellena de queso o carne.',2000,NULL,0,4.7,52
  UNION ALL SELECT 'marysabor@fritostech.local','empanadas','Empanadas de camarón','Empanadas crocantes rellenas de camarones guisados, típicas del Caribe.',3000,NULL,0,4.8,61
  UNION ALL SELECT 'matrona@fritostech.local','arepas-de-huevo','Arepa de huevo con carne','Arepa frita con huevo en el centro y relleno generoso de carne molida.',3000,NULL,0,4.8,73
  UNION ALL SELECT 'saborcaribe@fritostech.local','arepas-de-huevo','Arepa de huevo con queso','Arepa de huevo crujiente con mucho queso costeño derretido por dentro.',3000,NULL,0,4.7,55
  UNION ALL SELECT 'elsabor@fritostech.local','carimañola','Carimañolas de queso',NULL,2000,NULL,0,4.7,44
  UNION ALL SELECT 'esquina@fritostech.local','patacones','Patacón pisao',NULL,3000,NULL,0,4.8,69
  UNION ALL SELECT 'donarosa@fritostech.local','buñuelos','Buñuelos de frijol','Buñuelos del Caribe hechos con frijol cabecita negra, dorados y sabrosos.',1500,NULL,0,4.6,38
  UNION ALL SELECT 'rincon@fritostech.local','otros','Papa rellena','Bola de papa rellena de carne guisada, frita hasta quedar dorada.',2000,NULL,0,4.7,60
  UNION ALL SELECT 'donluis@fritostech.local','otros','Deditos de queso','Bastones de masa rellenos de queso que se derrite al morderlos.',1500,NULL,0,4.5,36
  UNION ALL SELECT 'delicia@fritostech.local','otros','Marranitas',NULL,1500,NULL,0,4.6,42
  UNION ALL SELECT 'sazonandino@fritostech.local','otros','Aborrajados',NULL,2000,NULL,0,4.8,57
  UNION ALL SELECT 'saborcaribe@fritostech.local','otros','Quibbes',NULL,2000,NULL,0,4.7,49
  UNION ALL SELECT 'rincon@fritostech.local','otros','Pastel de pollo',NULL,2000,NULL,0,4.6,35
  UNION ALL SELECT 'donarosa@fritostech.local','otros','Yuca frita',NULL,1500,NULL,0,4.5,31
  UNION ALL SELECT 'esquina@fritostech.local','otros','Tajadas de plátano maduro',NULL,1500,NULL,0,4.6,40
  UNION ALL SELECT 'donluis@fritostech.local','otros','Papas criollas fritas',NULL,1500,NULL,0,4.5,28
  UNION ALL SELECT 'matrona@fritostech.local','otros','Chicharrón',NULL,3000,NULL,0,4.8,66
  UNION ALL SELECT 'elsabor@fritostech.local','otros','Pasteles de yuca',NULL,2000,NULL,0,4.6,37
  UNION ALL SELECT 'saborcaribe@fritostech.local','otros','Arepa frita',NULL,1500,NULL,0,4.5,30
  UNION ALL SELECT 'sazonandino@fritostech.local','otros','Hojaldras',NULL,1500,NULL,0,4.6,34
  UNION ALL SELECT 'donarosa@fritostech.local','otros','Bolitas de yuca con queso',NULL,1500,NULL,0,4.7,46
  UNION ALL SELECT 'matrona@fritostech.local','otros','Arepa de choclo frita',NULL,3000,NULL,0,4.7,43
  UNION ALL SELECT 'marysabor@fritostech.local','otros','Cazón frito',NULL,3000,NULL,0,4.6,32
  UNION ALL SELECT 'esquina@fritostech.local','otros','Plátano relleno frito',NULL,3000,NULL,0,4.7,39
  UNION ALL SELECT 'donluis@fritostech.local','otros','Tostadas de plátano verde',NULL,1500,NULL,0,4.5,27
  UNION ALL SELECT 'rincon@fritostech.local','otros','Papa rellena con arroz y huevo',NULL,3000,NULL,0,4.8,51
) AS t
JOIN usuario   u ON u.correo = t.correo
JOIN categoria c ON c.slug   = t.slug;

-- Comprobación: debe devolver 38
-- SELECT COUNT(*) FROM producto;
