-- ══════════════════════════════════════════════════════════════════════
-- HogarFix · Patch: tabla de anuncios promocionales
-- Ejecutar una sola vez sobre hogarfix_db
-- ══════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS anuncios (
    id           INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    titulo       VARCHAR(120)    NOT NULL,
    mensaje      TEXT            NULL,
    imagen       VARCHAR(255)    NULL COMMENT 'URL completa o ruta /static/...',
    boton_texto  VARCHAR(60)     NULL,
    boton_link   VARCHAR(255)    NULL,
    activo       TINYINT(1)      NOT NULL DEFAULT 1,
    fecha_inicio DATETIME        NULL     COMMENT 'NULL = sin restricción de inicio',
    fecha_fin    DATETIME        NULL     COMMENT 'NULL = sin fecha de expiración',
    created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Anuncio de ejemplo (activo, sin fechas límite)
INSERT INTO anuncios (titulo, mensaje, boton_texto, boton_link, activo)
VALUES (
    '¡Bienvenido a HogarFix! 🎉',
    'Conectamos tu hogar con técnicos verificados en Bogotá. Reserva tu primer servicio hoy y experimenta la diferencia.',
    'Buscar técnico ahora',
    '/buscar',
    1
);
