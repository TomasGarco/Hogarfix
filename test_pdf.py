"""Script temporal para probar la generación del PDF del contrato."""
import json
from unittest.mock import MagicMock
from app.services.contract_pdf import generar_contrato_pdf

u = MagicMock()
u.id = 99
u.email = "tecnico@hogarfix.co"
u.full_name = "Prueba Tecnico"
u.address = "Calle 100 15-20"
u.locality = "Usaquen"
u.barrio = "Santa Barbara"
u.phone = "3001234567"
u.phone_country = "+57"

bio = json.dumps({
    "service_description": "Instalaciones electricas",
    "document_type": "CC",
    "document_number": "123456789",
})

p = MagicMock()
p.full_name = "Prueba Tecnico"
p.specialties = "Electricidad"
p.bio = bio
p.verification_status = "approved"
p.profile_photo = None

pdf_bytes = generar_contrato_pdf(u, p)
print(f"PDF generado OK, tamano: {len(pdf_bytes)} bytes")
with open("contrato_test.pdf", "wb") as f:
    f.write(pdf_bytes)
print("Guardado en contrato_test.pdf")
