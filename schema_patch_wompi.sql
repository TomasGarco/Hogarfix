-- ============================================================
-- HogarFix — Parche: integración Wompi (pagos digitales)
-- Ejecutar en phpMyAdmin sobre hogarfix_db
-- ============================================================

ALTER TABLE reservas
    ADD COLUMN IF NOT EXISTS wompi_transaction_id VARCHAR(100)  DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS wompi_status          VARCHAR(30)   DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS wompi_amount_cents    INT           DEFAULT NULL;
