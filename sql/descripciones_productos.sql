-- ============================================================
-- descripciones_productos.sql
-- Agrega la descripción corta a cada producto de FRITOS TECH.
-- EJECUTAR DESPUÉS de mis_productos.sql (y de tener los productos creados).
--
-- Busca cada producto por su nombre y actualiza la columna
-- descripcion. Es seguro ejecutarlo varias veces.
-- ============================================================

USE fritos_tech;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Permite UPDATE filtrando por nombre (MySQL Workbench lo bloquea por defecto)
SET SQL_SAFE_UPDATES = 0;

-- 1. Empanadas de carne
UPDATE producto SET descripcion = 'Empanadas crujientes de maíz rellenas de carne molida bien sazonada.' WHERE nombre = 'Empanadas de carne';

-- 2. Arepa de huevo
UPDATE producto SET descripcion = 'Arepa de maíz frita con un huevo entero en el centro, el clásico de la costa.' WHERE nombre = 'Arepa de huevo';

-- 3. Carimañolas de yuca
UPDATE producto SET descripcion = 'Masa de yuca en forma de torpedo, rellena de carne y frita hasta dorar.' WHERE nombre = 'Carimañolas de yuca';

-- 4. Patacones con hogao
UPDATE producto SET descripcion = 'Plátano verde frito y aplastado, acompañado de hogao casero de tomate y cebolla.' WHERE nombre = 'Patacones con hogao';

-- 5. Buñuelos
UPDATE producto SET descripcion = 'Bolitas de masa fritas, doradas por fuera y suaves por dentro.' WHERE nombre = 'Buñuelos';

-- 6. Empanada de pollo
UPDATE producto SET descripcion = 'Empanada dorada rellena de pollo desmechado con un toque criollo.' WHERE nombre = 'Empanada de pollo';

-- 7. Arepa de huevo especial
UPDATE producto SET descripcion = 'Arepa de huevo con relleno extra, más grande y llena de sabor.' WHERE nombre = 'Arepa de huevo especial';

-- 8. Patacón con queso
UPDATE producto SET descripcion = 'Patacón crocante cubierto con queso costeño rallado.' WHERE nombre = 'Patacón con queso';

-- 9. Empanadas de queso
UPDATE producto SET descripcion = 'Masa de maíz crujiente rellena de queso costeño derretido.' WHERE nombre = 'Empanadas de queso';

-- 10. Empanadas de pipián
UPDATE producto SET descripcion = 'Empanadas de papa y maní al estilo de Nariño, servidas con ají.' WHERE nombre = 'Empanadas de pipián';

-- 11. Empanadas vallecaucanas
UPDATE producto SET descripcion = 'Pequeñas empanadas de masa de maíz rellenas de carne y papa.' WHERE nombre = 'Empanadas vallecaucanas';

-- 12. Empanadas de cambray
UPDATE producto SET descripcion = 'Empanadas de masa de trigo, doradas y rellenas de carne o queso.' WHERE nombre = 'Empanadas de cambray';

-- 13. Empanadas de yuca
UPDATE producto SET descripcion = 'Masa suave de yuca frita, rellena de queso o carne.' WHERE nombre = 'Empanadas de yuca';

-- 14. Empanadas de camarón
UPDATE producto SET descripcion = 'Empanadas crocantes rellenas de camarones guisados, típicas del Caribe.' WHERE nombre = 'Empanadas de camarón';

-- 15. Arepa de huevo con carne
UPDATE producto SET descripcion = 'Arepa frita con huevo en el centro y relleno generoso de carne molida.' WHERE nombre = 'Arepa de huevo con carne';

-- 16. Arepa de huevo con queso
UPDATE producto SET descripcion = 'Arepa de huevo crujiente con mucho queso costeño derretido por dentro.' WHERE nombre = 'Arepa de huevo con queso';

-- 17. Carimañolas de queso
UPDATE producto SET descripcion = 'Masa de yuca frita rellena de queso suave que se derrite al morder.' WHERE nombre = 'Carimañolas de queso';

-- 18. Patacón pisao
UPDATE producto SET descripcion = 'Plátano verde aplastado y frito dos veces, crocante y con sal justa.' WHERE nombre = 'Patacón pisao';

-- 19. Buñuelos de frijol
UPDATE producto SET descripcion = 'Buñuelos del Caribe hechos con frijol cabecita negra, dorados y sabrosos.' WHERE nombre = 'Buñuelos de frijol';

-- 20. Papa rellena
UPDATE producto SET descripcion = 'Bola de papa rellena de carne guisada, frita hasta quedar dorada.' WHERE nombre = 'Papa rellena';

-- 21. Deditos de queso
UPDATE producto SET descripcion = 'Bastones de masa rellenos de queso que se derrite al morderlos.' WHERE nombre = 'Deditos de queso';

-- 22. Marranitas
UPDATE producto SET descripcion = 'Plátano maduro frito relleno de chicharrón, dulce y salado a la vez.' WHERE nombre = 'Marranitas';

-- 23. Aborrajados
UPDATE producto SET descripcion = 'Plátano maduro con queso, apanado y frito hasta quedar crujiente.' WHERE nombre = 'Aborrajados';

-- 24. Quibbes
UPDATE producto SET descripcion = 'Croquetas de trigo y carne con especias, herencia árabe del Caribe.' WHERE nombre = 'Quibbes';

-- 25. Pastel de pollo
UPDATE producto SET descripcion = 'Pastel hojaldrado y dorado relleno de pollo guisado con verduras.' WHERE nombre = 'Pastel de pollo';

-- 26. Yuca frita
UPDATE producto SET descripcion = 'Bastones de yuca fritos, crujientes por fuera y suaves por dentro.' WHERE nombre = 'Yuca frita';

-- 27. Tajadas de plátano maduro
UPDATE producto SET descripcion = 'Rodajas de plátano maduro fritas, caramelizadas y dulces.' WHERE nombre = 'Tajadas de plátano maduro';

-- 28. Papas criollas fritas
UPDATE producto SET descripcion = 'Papitas criollas amarillas fritas enteras, doradas y con sal.' WHERE nombre = 'Papas criollas fritas';

-- 29. Chicharrón
UPDATE producto SET descripcion = 'Trozos de cerdo fritos, bien crocantes por fuera y jugosos por dentro.' WHERE nombre = 'Chicharrón';

-- 30. Pasteles de yuca
UPDATE producto SET descripcion = 'Pasteles de masa de yuca rellenos de carne o queso, fritos al momento.' WHERE nombre = 'Pasteles de yuca';

-- 31. Arepa frita
UPDATE producto SET descripcion = 'Arepa de maíz frita, inflada y dorada, perfecta para acompañar.' WHERE nombre = 'Arepa frita';

-- 32. Hojaldras
UPDATE producto SET descripcion = 'Masa de trigo frita, aireada y ligera, ideal para el desayuno.' WHERE nombre = 'Hojaldras';

-- 33. Bolitas de yuca con queso
UPDATE producto SET descripcion = 'Bolitas de yuca rellenas de queso, crujientes y bien suaves por dentro.' WHERE nombre = 'Bolitas de yuca con queso';

-- 34. Arepa de choclo frita
UPDATE producto SET descripcion = 'Arepa de maíz tierno frita, ligeramente dulce y con queso.' WHERE nombre = 'Arepa de choclo frita';

-- 35. Cazón frito
UPDATE producto SET descripcion = 'Trozos de cazón apanados y fritos, frescos del mar Caribe.' WHERE nombre = 'Cazón frito';

-- 36. Plátano relleno frito
UPDATE producto SET descripcion = 'Plátano frito relleno de carne o queso, dulce por fuera y sabroso por dentro.' WHERE nombre = 'Plátano relleno frito';

-- 37. Tostadas de plátano verde
UPDATE producto SET descripcion = 'Láminas finas de plátano verde fritas, crocantes y saladas.' WHERE nombre = 'Tostadas de plátano verde';

-- 38. Papa rellena con arroz y huevo
UPDATE producto SET descripcion = 'Papa rellena con carne, arroz y huevo cocido, una versión más contundente.' WHERE nombre = 'Papa rellena con arroz y huevo';

SET SQL_SAFE_UPDATES = 1;

-- ------------------------------------------------------------
-- Verificación: debe devolver 0 filas. Si sale alguna, ese producto
-- no tiene descripción (su nombre no coincide con el de este archivo).
-- ------------------------------------------------------------
SELECT id, nombre
FROM producto
WHERE descripcion IS NULL OR descripcion = '';
