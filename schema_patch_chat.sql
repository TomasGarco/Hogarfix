-- ============================================================
-- HogarFix — Parche: chat directo por reserva
-- Ejecutar en phpMyAdmin sobre la base de datos hogarfix_db
-- ============================================================

CREATE TABLE IF NOT EXISTS booking_messages (
    id          INT          NOT NULL AUTO_INCREMENT,
    booking_id  INT          NOT NULL,
    sender_id   INT          NOT NULL,
    content     TEXT         NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read     TINYINT(1)   NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    INDEX idx_bm_booking (booking_id),
    INDEX idx_bm_sender  (sender_id),
    CONSTRAINT fk_bm_booking FOREIGN KEY (booking_id) REFERENCES reservas(id)  ON DELETE CASCADE,
    CONSTRAINT fk_bm_sender  FOREIGN KEY (sender_id)  REFERENCES usuarios(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
