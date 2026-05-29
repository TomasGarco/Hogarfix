-- Patch: flujo de evidencia de servicio completado
-- Ejecutar contra hogarfix_db

ALTER TABLE reservas
  ADD COLUMN IF NOT EXISTS evidence_photos TEXT NOT NULL DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS completion_note TEXT NOT NULL DEFAULT '';
