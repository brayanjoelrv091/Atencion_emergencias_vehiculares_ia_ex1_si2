-- Añadir a la tabla de usuarios existente
ALTER TABLE usuarios ADD COLUMN intentos_fallidos INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE usuarios ADD COLUMN bloqueado_hasta TIMESTAMP WITH TIME ZONE;
