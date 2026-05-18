CREATE USER IF NOT EXISTS 'app_deportes'@'%' IDENTIFIED BY 'app_deportes_2026';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON actividades_deportivas.* TO 'app_deportes'@'%';
FLUSH PRIVILEGES;
