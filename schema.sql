-- ============================================================
-- HOGARFIX — SCHEMA UNIFICADO v2.0
-- Base + OAuth + avatar + suspensión + policy_acceptances
-- Última actualización: 2026-05-22
-- ============================================================
-- INSTRUCCIONES DE IMPORTACIÓN
--   Importar desde phpMyAdmin ➜ pestaña SQL ➜ pegar y ejecutar.
--   El script recrea la base de datos desde cero en cada ejecución.
-- ============================================================

CREATE DATABASE IF NOT EXISTS hogarfix_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE hogarfix_db;

-- ── Limpiar tablas en orden inverso de dependencias ─────────
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS policy_acceptances;
DROP TABLE IF EXISTS otp_verifications;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS logs_login;
DROP TABLE IF EXISTS notificaciones;
DROP TABLE IF EXISTS resenas;
DROP TABLE IF EXISTS disponibilidad;
DROP TABLE IF EXISTS reservas;
DROP TABLE IF EXISTS tecnicos;
DROP TABLE IF EXISTS usuarios;
SET FOREIGN_KEY_CHECKS = 1;


-- ============================================================
-- 1. TABLAS PRINCIPALES
-- ============================================================

-- ── Usuarios (admin, técnico, cliente) ──────────────────────
CREATE TABLE usuarios (
    id                    INT AUTO_INCREMENT  PRIMARY KEY,
    email                 VARCHAR(120)        NOT NULL UNIQUE,
    password_hash         VARCHAR(255)        NOT NULL,
    role                  ENUM('admin','tecnico','cliente') NOT NULL,
    full_name             VARCHAR(120)        NULL,
    phone                 VARCHAR(20)         NULL,
    phone_country         VARCHAR(10)         NULL DEFAULT '+57',
    locality              VARCHAR(120)        NULL,
    barrio                VARCHAR(120)        NULL,
    address               VARCHAR(180)        NULL,
    phone_verified        TINYINT(1)          NOT NULL DEFAULT 0,
    notifications_enabled TINYINT(1)          NOT NULL DEFAULT 1,
    two_factor_enabled    TINYINT(1)          NOT NULL DEFAULT 1,
    accepted_terms        TINYINT(1)          NOT NULL DEFAULT 0,
    accepted_terms_at     DATETIME            NULL,
    is_active             TINYINT(1)          NOT NULL DEFAULT 1,
    -- Login social (Google OAuth / OpenID Connect)
    oauth_provider        VARCHAR(30)         NULL,
    oauth_subject         VARCHAR(255)        NULL,
    avatar_url            VARCHAR(255)        NULL,
    created_at            DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Perfil del técnico ───────────────────────────────────────
CREATE TABLE tecnicos (
    id                   INT AUTO_INCREMENT  PRIMARY KEY,
    user_id              INT                 NOT NULL UNIQUE,
    full_name            VARCHAR(120)        NOT NULL,
    bio                  TEXT,
    specialties          VARCHAR(255),
    localities           VARCHAR(255),
    price_range          VARCHAR(80),
    technician_type      VARCHAR(30)         NOT NULL,
    profile_photo        VARCHAR(255),
    work_photos          TEXT,
    verification_id_front  VARCHAR(255),
    verification_id_back   VARCHAR(255),
    verification_selfie    VARCHAR(255),
    verification_status  VARCHAR(30)         NOT NULL DEFAULT 'pending',
    -- Suspensión
    suspended_at         DATETIME            NULL DEFAULT NULL,
    suspension_reason    VARCHAR(255)        NULL DEFAULT NULL,
    suspension_type      VARCHAR(20)         NULL DEFAULT NULL,   -- 'temporal' | 'definitiva'
    created_at           DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tecnico_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Reservas ─────────────────────────────────────────────────
CREATE TABLE reservas (
    id             INT AUTO_INCREMENT  PRIMARY KEY,
    client_id      INT                 NOT NULL,
    technician_id  INT                 NOT NULL,
    service_type   VARCHAR(80)         NOT NULL,
    locality       VARCHAR(120)        NOT NULL,
    booking_date   DATE                NOT NULL,
    booking_time   TIME                NOT NULL,
    notes          TEXT,
    status         VARCHAR(20)         NOT NULL DEFAULT 'pendiente',
    created_at     DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reserva_cliente  FOREIGN KEY (client_id)     REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reserva_tecnico  FOREIGN KEY (technician_id) REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Disponibilidad (slots del técnico) ───────────────────────
CREATE TABLE disponibilidad (
    id             INT AUTO_INCREMENT  PRIMARY KEY,
    technician_id  INT                 NOT NULL,
    date           DATE                NOT NULL,
    start_time     TIME                NOT NULL,
    end_time       TIME                NOT NULL,
    is_booked      TINYINT(1)          NOT NULL DEFAULT 0,
    UNIQUE KEY uq_disponibilidad_slot (technician_id, date, start_time),
    CONSTRAINT fk_disponibilidad_tecnico FOREIGN KEY (technician_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Reseñas ──────────────────────────────────────────────────
CREATE TABLE resenas (
    id             INT AUTO_INCREMENT  PRIMARY KEY,
    booking_id     INT                 NOT NULL UNIQUE,
    client_id      INT                 NOT NULL,
    technician_id  INT                 NOT NULL,
    rating         TINYINT UNSIGNED    NOT NULL,
    comment        TEXT,
    created_at     DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_resena_booking  FOREIGN KEY (booking_id)    REFERENCES reservas(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resena_cliente  FOREIGN KEY (client_id)     REFERENCES usuarios(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_resena_tecnico  FOREIGN KEY (technician_id) REFERENCES usuarios(id)  ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================================
-- 2. TABLAS DE SEGURIDAD / SESIONES
-- ============================================================

-- ── Log de inicios de sesión ─────────────────────────────────
CREATE TABLE logs_login (
    id          INT AUTO_INCREMENT  PRIMARY KEY,
    user_id     INT                 NULL,
    ip_address  VARCHAR(80),
    user_agent  VARCHAR(255),
    login_at    DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_log_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Sesiones activas ─────────────────────────────────────────
CREATE TABLE user_sessions (
    id             INT AUTO_INCREMENT  PRIMARY KEY,
    user_id        INT                 NOT NULL,
    session_token  VARCHAR(64)         NOT NULL UNIQUE,
    ip_address     VARCHAR(80),
    user_agent     VARCHAR(255),
    last_seen_at   DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at     DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at     DATETIME            NULL,
    CONSTRAINT fk_user_session_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Códigos OTP ──────────────────────────────────────────────
CREATE TABLE otp_verifications (
    id                   INT AUTO_INCREMENT  PRIMARY KEY,
    user_id              INT                 NOT NULL,
    code_hash            VARCHAR(64)         NOT NULL,
    salt                 VARCHAR(64)         NOT NULL,
    expires_at           DATETIME            NOT NULL,
    attempts             INT                 NOT NULL DEFAULT 0,
    max_attempts         INT                 NOT NULL DEFAULT 5,
    resend_count         INT                 NOT NULL DEFAULT 1,
    resend_window_start  DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivery_channel     VARCHAR(20)         NOT NULL DEFAULT 'email',
    last_sent_at         DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at           DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_otp_user (user_id),
    CONSTRAINT fk_otp_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================================
-- 3. TABLAS DE COMUNICACIÓN
-- ============================================================

-- ── Notificaciones in-app ────────────────────────────────────
CREATE TABLE notificaciones (
    id          INT AUTO_INCREMENT  PRIMARY KEY,
    user_id     INT                 NOT NULL,
    type        VARCHAR(30)         NOT NULL DEFAULT 'general',
    title       VARCHAR(120)        NOT NULL,
    message     TEXT                NOT NULL,
    link_url    VARCHAR(255)        NULL,
    is_read     TINYINT(1)          NOT NULL DEFAULT 0,
    created_at  DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notificacion_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ── Aceptación de políticas ──────────────────────────────────
CREATE TABLE policy_acceptances (
    id              INT AUTO_INCREMENT  PRIMARY KEY,
    user_id         INT                 NOT NULL,
    policy_version  VARCHAR(10)         NOT NULL DEFAULT '1.0',
    ip_address      VARCHAR(80)         NULL,
    accepted_at     DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_policy_usuario FOREIGN KEY (user_id)
        REFERENCES usuarios(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- ============================================================
-- 4. ÍNDICES DE RENDIMIENTO
-- ============================================================

CREATE INDEX idx_usuarios_role            ON usuarios(role);
CREATE INDEX idx_usuarios_created_at      ON usuarios(created_at);
CREATE INDEX idx_usuarios_oauth           ON usuarios(oauth_provider, oauth_subject);
CREATE INDEX idx_reservas_cliente_estado  ON reservas(client_id, status);
CREATE INDEX idx_reservas_tecnico_estado  ON reservas(technician_id, status);
CREATE INDEX idx_reservas_fecha           ON reservas(booking_date, booking_time);
CREATE INDEX idx_disponibilidad_fecha     ON disponibilidad(technician_id, date);
CREATE INDEX idx_logs_login_user_date     ON logs_login(user_id, login_at);
CREATE INDEX idx_notificaciones_user_read ON notificaciones(user_id, is_read, created_at);
CREATE INDEX idx_user_sessions_active     ON user_sessions(user_id, revoked_at, last_seen_at);
CREATE INDEX idx_otp_expires_at           ON otp_verifications(expires_at);
CREATE INDEX idx_policy_user              ON policy_acceptances(user_id);
CREATE INDEX idx_policy_version           ON policy_acceptances(policy_version);


-- ============================================================
-- 5. DATOS INICIALES — USUARIOS DEL SISTEMA
-- ============================================================

-- ── Admin principal ──────────────────────────────────────────
-- Contraseña real: ver variable FLASK_ADMIN_PASS (configurada al instalar)
INSERT INTO usuarios (email, password_hash, role, full_name, is_active, accepted_terms, accepted_terms_at)
VALUES (
    'tomasgarcia1826@gmail.com',
    'scrypt:32768:8:1$tyuo2GB5WV34Upib$c2790690625a9fe620cfd59c62d82246f9d05bcc83e8c26bffb344024bddcfc6e1fdeaf5a1a5c70829f844e575f30f1092fe559befd0071cf59ddb88680bb48a',
    'admin',
    'Administrador HogarFix',
    1, 1, NOW()
)
ON DUPLICATE KEY UPDATE
    password_hash     = VALUES(password_hash),
    role              = VALUES(role),
    full_name         = VALUES(full_name),
    is_active         = VALUES(is_active),
    accepted_terms    = VALUES(accepted_terms),
    accepted_terms_at = VALUES(accepted_terms_at);


-- ============================================================
-- 6. DATOS DE PRUEBA (DEV ONLY — eliminar en producción)
-- ============================================================
-- Técnico demo:  tecnico@hogarfix.co  /  tecnico2026
-- Cliente demo:  cliente@hogarfix.co  /  cliente2026
-- ────────────────────────────────────────────────────────────

-- ── Usuario técnico de prueba ────────────────────────────────
INSERT INTO usuarios (email, password_hash, role, full_name, locality, is_active, accepted_terms, accepted_terms_at)
VALUES (
    'tecnico@hogarfix.co',
    'scrypt:32768:8:1$pqrFXthsnmiL08gw$5c0c06698aaf03de53c3e63e993be47eee30b57f7478f0827a19beec69b91b400c5f1ef9c4f94383d11d3f8bf41c3b55e528e6b5b617a139d8db2d36c4bf0bd3',
    'tecnico',
    'Carlos Rodríguez',
    'Suba',
    1, 1, NOW()
)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- ── Perfil del técnico ───────────────────────────────────────
INSERT INTO tecnicos (user_id, full_name, bio, specialties, localities, price_range, technician_type, verification_status)
SELECT id,
    'Carlos Rodríguez',
    'Electricista certificado con 8 años de experiencia en instalaciones residenciales y comerciales.',
    '["Electricidad","Instalaciones","Domotica"]',
    '["Suba","Engativa","Chapinero","Usaquén"]',
    '50000-150000',
    'electricista',
    'approved'
FROM usuarios WHERE email = 'tecnico@hogarfix.co'
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- ── Usuario cliente de prueba ────────────────────────────────
INSERT INTO usuarios (email, password_hash, role, full_name, locality, is_active, accepted_terms, accepted_terms_at)
VALUES (
    'cliente@hogarfix.co',
    'scrypt:32768:8:1$AR7CThk7DcbcLekI$8d6001a22d38e9879cd6f5966f1d9f2d02631f5eb940622518a2bb615f5af256b81cb094d226062abadbe3d4ac343daa35da87d67b50db752355e7b7bdf12694',
    'cliente',
    'María Gómez',
    'Chapinero',
    1, 1, NOW()
)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);


-- ── Disponibilidad del técnico (próximas 2 semanas) ──────────
-- Slots libres: lunes a viernes, mañana (08:00–12:00) y tarde (14:00–18:00)
INSERT INTO disponibilidad (technician_id, date, start_time, end_time, is_booked)
SELECT
    u.id,
    DATE_ADD(CURDATE(), INTERVAL n DAY),
    t.start_time,
    t.end_time,
    0
FROM usuarios u
JOIN (
    SELECT 0 AS n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4
    UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11
) days ON DAYOFWEEK(DATE_ADD(CURDATE(), INTERVAL days.n DAY)) BETWEEN 2 AND 6
JOIN (
    SELECT '08:00:00' AS start_time, '10:00:00' AS end_time UNION ALL
    SELECT '10:00:00',               '12:00:00'             UNION ALL
    SELECT '14:00:00',               '16:00:00'             UNION ALL
    SELECT '16:00:00',               '18:00:00'
) t ON 1=1
WHERE u.email = 'tecnico@hogarfix.co'
ON DUPLICATE KEY UPDATE is_booked = is_booked;

-- ── Reservas de ejemplo (visibles en el calendario) ──────────
INSERT INTO reservas (client_id, technician_id, service_type, locality, booking_date, booking_time, notes, status)
SELECT
    c.id,
    t.id,
    datos.service_type,
    datos.locality,
    DATE_ADD(CURDATE(), INTERVAL datos.dias DAY),
    datos.hora,
    datos.notas,
    datos.status
FROM usuarios c
JOIN  usuarios t ON t.email = 'tecnico@hogarfix.co'
JOIN (
    SELECT 1 AS dias, '09:00:00' AS hora, 'Electricidad'  AS service_type, 'Suba'       AS locality, 'Revisar panel eléctrico'      AS notas, 'confirmado' AS status UNION ALL
    SELECT 1,         '14:00:00',         'Electricidad',                   'Suba',       'Instalar toma corriente nuevo',               'pendiente'  UNION ALL
    SELECT 2,         '10:00:00',         'Iluminación',                    'Engativa',   'Cambio de luminarias LED',                    'confirmado' UNION ALL
    SELECT 3,         '08:00:00',         'Domotica',                       'Chapinero',  'Instalación de sensores de movimiento',       'pendiente'  UNION ALL
    SELECT 5,         '09:00:00',         'Electricidad',                   'Usaquén',    'Revisión instalación cableado',               'pendiente'  UNION ALL
    SELECT 7,         '14:00:00',         'Iluminación',                    'Suba',       'Diagnóstico planta eléctrica',                'confirmado' UNION ALL
    SELECT 8,         '10:00:00',         'Electricidad',                   'Engativa',   'Cortocircuito en cocina',                     'cancelado'  UNION ALL
    SELECT 9,         '08:00:00',         'Domotica',                       'Chapinero',  'Configurar sistema de domótica',              'pendiente'
) datos ON 1=1
WHERE c.email = 'cliente@hogarfix.co';

-- Marcar como ocupados los slots que ya tienen reserva
UPDATE disponibilidad d
JOIN reservas r
    ON  r.technician_id = d.technician_id
    AND r.booking_date  = d.date
    AND r.booking_time  >= d.start_time
    AND r.booking_time  <  d.end_time
SET d.is_booked = 1
WHERE r.status != 'cancelado';

