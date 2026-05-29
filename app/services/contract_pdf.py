"""
Generador de contrato de prestacion de servicios en PDF.
Usa fpdf2. Blanco y negro, formato legal profesional con logo.
"""

import json
import os
from datetime import datetime
from io import BytesIO

from fpdf import FPDF, XPos, YPos


# Paleta blanco y negro
NEGRO      = (20, 20, 20)
GRIS_OSC   = (80, 80, 80)
GRIS_MED   = (150, 150, 150)
GRIS_CLAR  = (220, 220, 220)
BLANCO     = (255, 255, 255)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "img", "logo-hogarfix.svg")


class ContratoHogarFix(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(25, 28, 25)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Línea superior fina
        self.set_draw_color(*GRIS_MED)
        self.set_line_width(0.5)
        self.line(25, 10, 185, 10)

        # Logo SVG (si existe y fpdf2 lo soporta)
        logo = os.path.normpath(LOGO_PATH)
        if os.path.exists(logo):
            try:
                self.image(logo, x=25, y=12, h=9)
            except Exception:
                self._logo_texto()
        else:
            self._logo_texto()

        # Texto derecho del encabezado
        self.set_xy(0, 13)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*GRIS_OSC)
        self.cell(0, 4, "hogarfix.co  ·  soporte@hogarfix.co  ·  Bogota, Colombia", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_draw_color(*GRIS_MED)
        self.line(25, 24, 185, 24)
        self.set_text_color(*NEGRO)
        self.ln(8)

    def _logo_texto(self):
        self.set_xy(25, 12)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*NEGRO)
        self.cell(60, 8, "HogarFix", new_x=XPos.RIGHT, new_y=YPos.LAST)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*GRIS_MED)
        self.set_line_width(0.3)
        self.line(25, self.get_y(), 185, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GRIS_MED)
        self.cell(0, 5, f"HogarFix · Contrato de Prestacion de Servicios · Pagina {self.page_no()} de {{nb}}", align="C")

    def section_title(self, title: str):
        self.ln(2)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*NEGRO)
        self.cell(0, 6, title.upper(), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Línea bajo el título
        self.set_draw_color(*GRIS_MED)
        self.set_line_width(0.3)
        self.line(25, self.get_y(), 185, self.get_y())
        self.ln(3)
        self.set_text_color(*NEGRO)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*NEGRO)
        self.multi_cell(0, 5.5, text, align="J")
        self.ln(2)

    def field_row(self, label: str, value: str):
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*NEGRO)
        self.cell(58, 5.5, label + ":", new_x=XPos.RIGHT, new_y=YPos.LAST)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(*GRIS_OSC)
        self.cell(0, 5.5, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*NEGRO)


def _safe(val, default="No especificado"):
    if not val or str(val).strip() in ("", "None"):
        return default
    return str(val).strip()


def generar_contrato_pdf(user, profile) -> bytes:
    """
    Genera el PDF del contrato de prestacion de servicios.
    Recibe un User y su TechnicianProfile.
    Retorna bytes del PDF.
    """
    meta = {}
    if profile and profile.bio:
        try:
            meta = json.loads(profile.bio)
        except Exception:
            meta = {}

    pdf = ContratoHogarFix()
    pdf.alias_nb_pages()
    pdf.add_page()

    fecha = datetime.now().strftime("%d de %B de %Y").replace(
        "January", "enero").replace("February", "febrero").replace(
        "March", "marzo").replace("April", "abril").replace(
        "May", "mayo").replace("June", "junio").replace(
        "July", "julio").replace("August", "agosto").replace(
        "September", "septiembre").replace("October", "octubre").replace(
        "November", "noviembre").replace("December", "diciembre")

    # ─── ENCABEZADO DEL DOCUMENTO ───
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*NEGRO)
    pdf.cell(0, 10, "CONTRATO DE PRESTACION DE SERVICIOS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRIS_OSC)
    pdf.cell(0, 6, f"Bogota, Colombia · {fecha}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # Numero de contrato
    contrato_num = f"HF-{user.id:05d}-{datetime.now().strftime('%Y%m')}"
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*GRIS_MED)
    pdf.cell(0, 5, f"N\u00b0 Contrato: {contrato_num}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ─── PARTES ───
    pdf.section_title("1. PARTES DEL CONTRATO")
    pdf.body_text(
        "El presente contrato se celebra entre HogarFix (en adelante 'LA PLATAFORMA'), "
        "con domicilio en la ciudad de Bogota, Colombia, representada digitalmente a traves "
        "del sitio web hogarfix.co, y el TECNICO INDEPENDIENTE que se identifica a continuacion "
        "(en adelante 'EL TECNICO')."
    )

    full_name = _safe(profile.full_name if profile else user.full_name, "No registrado")
    doc_type = _safe(meta.get("document_type"), "").upper()
    doc_number = _safe(meta.get("document_number"))
    address = _safe(meta.get("technician_address") or user.address)
    locality = _safe(user.locality)
    barrio = _safe(user.barrio)
    phone = f"{_safe(user.phone_country, '')} {_safe(user.phone)}".strip()
    email = _safe(user.email)

    pdf.field_row("Nombre completo", full_name)
    pdf.field_row("Tipo de documento", doc_type if doc_type else "No especificado")
    pdf.field_row("Numero de documento", doc_number)
    pdf.field_row("Direccion", f"{address}, {barrio}, {locality}")
    pdf.field_row("Telefono", phone)
    pdf.field_row("Correo electronico", email)
    pdf.ln(3)

    # ─── OBJETO ───
    pdf.section_title("2. OBJETO DEL CONTRATO")
    specialty = _safe(profile.specialties if profile else "", "Servicios tecnicos del hogar")
    service_desc = _safe(meta.get("service_description"), "Prestacion de servicios tecnicos del hogar.")
    pdf.body_text(
        f"EL TECNICO se compromete a prestar servicios de {specialty} a traves de la plataforma "
        f"HogarFix, conectando con clientes que requieran servicios del hogar en la ciudad de Bogota. "
        f"Descripcion de servicios: {service_desc}"
    )

    # ─── CONDICIONES DE SERVICIO ───
    pdf.section_title("3. CONDICIONES DE PRESTACION DEL SERVICIO")
    charge_type = _safe(meta.get("charge_type"), "Por servicio")
    base_price = _safe(meta.get("base_price"))
    days = ", ".join(meta.get("availability_days") or ["No especificado"])
    start_t = _safe(meta.get("availability_start"))
    end_t = _safe(meta.get("availability_end"))
    years_exp = _safe(meta.get("years_experience") or meta.get("service_description"))

    pdf.field_row("Modalidad de cobro", charge_type.capitalize())
    pdf.field_row("Precio base", f"COP ${base_price}" if base_price != "No especificado" else "No especificado")
    pdf.field_row("Dias disponibles", days)
    pdf.field_row("Horario", f"{start_t} - {end_t}" if start_t != "No especificado" else "No especificado")
    pdf.ln(3)

    # ─── OBLIGACIONES ───
    pdf.section_title("4. OBLIGACIONES DE EL TECNICO")
    obligaciones = [
        "Prestar los servicios acordados con calidad, responsabilidad y respeto hacia los clientes.",
        "Mantener su perfil actualizado con informacion veridica en la plataforma HogarFix.",
        "Cumplir los horarios y compromisos pactados con los clientes.",
        "No divulgar informacion confidencial de los clientes obtenida a traves de la plataforma.",
        "Contar con herramientas, competencias y certificaciones necesarias para los servicios ofrecidos.",
        "Tratar a los clientes con dignidad, honestidad y buen trato en todo momento.",
        "Informar a HogarFix cualquier incidente relevante ocurrido durante la prestacion del servicio.",
        "Cumplir con la normativa vigente en Colombia para la prestacion de servicios tecnicos.",
    ]
    texto_obligaciones = "\n".join(f"{i}. {ob}" for i, ob in enumerate(obligaciones, 1))
    pdf.body_text(texto_obligaciones)
    pdf.ln(2)

    # ─── OBLIGACIONES PLATAFORMA ───
    pdf.section_title("5. OBLIGACIONES DE LA PLATAFORMA")
    pdf.body_text(
        "HogarFix se compromete a: (a) Proporcionar al TECNICO acceso a la plataforma digital "
        "para la gestion de servicios. (b) Proteger los datos personales del TECNICO conforme "
        "a la Ley 1581 de 2012 y su Politica de Privacidad. (c) Gestionar los pagos de manera "
        "transparente segun las condiciones pactadas. (d) Brindar soporte tecnico y operativo "
        "al TECNICO para el uso de la plataforma."
    )

    # ─── REMUNERACION ───
    pdf.section_title("6. REMUNERACION Y PAGOS")
    pdf.body_text(
        "EL TECNICO recibira como contraprestacion por sus servicios el valor acordado con el "
        "cliente, descontando la comision de plataforma vigente segun los terminos y condiciones "
        "de HogarFix publicados en hogarfix.co. Los pagos se realizaran a traves de los "
        "mecanismos digitales habilitados por la plataforma."
    )

    # ─── PROTECCION DE DATOS ───
    pdf.section_title("7. TRATAMIENTO DE DATOS PERSONALES")
    pdf.body_text(
        "De conformidad con la Ley 1581 de 2012 (Habeas Data), EL TECNICO autoriza a HogarFix "
        "el tratamiento de sus datos personales para: la gestion del contrato, la prestacion del "
        "servicio, el envio de comunicaciones relacionadas con la plataforma, y el cumplimiento "
        "de obligaciones legales. EL TECNICO podra ejercer sus derechos de acceso, correccion, "
        "supresion y portabilidad escribiendo a soporte@hogarfix.co."
    )

    # ─── DURACION ───
    pdf.section_title("8. DURACION Y TERMINACION")
    pdf.body_text(
        "El presente contrato tiene vigencia indefinida a partir de la fecha de aceptacion digital "
        "por parte de EL TECNICO. Cualquiera de las partes podra dar por terminado el contrato "
        "con aviso previo de 15 dias calendario. HogarFix se reserva el derecho de suspender "
        "o cancelar la cuenta del TECNICO en casos de incumplimiento grave, fraude o conductas "
        "que afecten la confianza de los usuarios de la plataforma."
    )

    # ─── INDEPENDENCIA ───
    pdf.section_title("9. NATURALEZA DEL CONTRATO")
    pdf.body_text(
        "El presente contrato es de naturaleza civil y comercial. EL TECNICO actua como "
        "contratista independiente y no existe relacion laboral, ni vinculo de subordinacion, "
        "con HogarFix. EL TECNICO es responsable del pago de sus propios impuestos, seguridad "
        "social y obligaciones legales derivadas de su actividad como independiente."
    )

    # ─── PENALIZACIONES ───
    pdf.section_title("10. PENALIZACIONES POR INCUMPLIMIENTO")
    pdf.body_text(
        "El incumplimiento de las obligaciones establecidas en el presente contrato dara lugar "
        "a las siguientes consecuencias, segun la gravedad:"
    )
    pdf.body_text(
        "a) SUSPENSION TEMPORAL: Calificacion promedio inferior a 2.5 estrellas sostenida por "
        "30 dias calendario. La cuenta sera suspendida temporalmente hasta mejorar el indicador. "
        "Durante la suspension, EL TECNICO no podra recibir nuevos servicios.\n\n"
        "b) CANCELACION DE CONTRATO: Calificacion promedio inferior a 2.0 estrellas por 60 dias "
        "calendario, o incumplimiento grave documentado (fraude, dano a bienes del cliente, "
        "conducta inapropiada). HogarFix notificara al TECNICO con al menos 5 dias de antelacion.\n\n"
        "c) PENALIZACION ECONOMICA: El incumplimiento reiterado de compromisos pactados con "
        "clientes (cancelaciones sin aviso, no presentacion) podra dar lugar a la retencion de "
        "hasta el 15% del valor del servicio afectado como compensacion al cliente, descontada "
        "de pagos futuros del TECNICO.\n\n"
        "d) ACCIONES LEGALES: En casos de fraude comprobado, danos materiales o conductas "
        "delictivas, HogarFix se reserva el derecho de iniciar las acciones legales pertinentes "
        "ante las autoridades competentes de la Republica de Colombia, de conformidad con el "
        "Codigo Civil, el Codigo Penal y la normativa vigente."
    )

    # ─── RENOVACION ───
    pdf.section_title("11. RENOVACION Y EVALUACION DEL CONTRATO")
    pdf.body_text(
        "El contrato se mantiene vigente de forma indefinida siempre que EL TECNICO cumpla con "
        "los estandares de calidad de la plataforma. HogarFix evaluara periodicamente el "
        "desempeno del TECNICO con base en: calificaciones de clientes, tasa de cumplimiento "
        "de servicios, tiempo de respuesta y quejas recibidas. Un desempeno sobresaliente "
        "(calificacion >= 4.5 estrellas sostenida) podra dar lugar a beneficios adicionales "
        "como mayor visibilidad en resultados de busqueda y distintivo de 'Tecnico Destacado'."
    )

    # ─── LEY APLICABLE ───
    pdf.section_title("12. LEY APLICABLE Y JURISDICCION")
    pdf.body_text(
        "El presente contrato se rige por las leyes de la Republica de Colombia, incluyendo "
        "la Ley 527 de 1999 (Comercio Electronico), la Ley 1581 de 2012 (Proteccion de Datos) "
        "y el Codigo Civil. Cualquier controversia sera resuelta, en primera instancia, mediante "
        "mecanismos alternativos de solucion de conflictos. En caso de no llegar a un acuerdo, "
        "las partes se someten a los jueces competentes de la ciudad de Bogota D.C."
    )

    # ─── FIRMA ───
    pdf.add_page()
    pdf.section_title("13. ACEPTACION Y FIRMA DIGITAL")
    pdf.body_text(
        "EL TECNICO declara haber leido, comprendido y aceptado la totalidad de los terminos "
        "y condiciones del presente contrato, manifestando su consentimiento libre e informado "
        "mediante firma digital en la plataforma HogarFix."
    )
    pdf.ln(4)

    # Cuadro de firma
    pdf.set_draw_color(*GRIS_MED)
    pdf.set_line_width(0.4)
    pdf.rect(25, pdf.get_y(), 75, 45)
    pdf.rect(110, pdf.get_y(), 75, 45)

    y_box = pdf.get_y()

    # Firma del técnico - si hay imagen de firma
    pdf.set_xy(25, y_box + 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*NEGRO)
    pdf.cell(75, 5, "EL TECNICO", align="C")

    signature_data = meta.get("signature_data", "")
    if signature_data and signature_data.startswith("data:image/png;base64,"):
        import base64
        import tempfile
        try:
            img_bytes = base64.b64decode(signature_data.split(",", 1)[1])
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=30, y=y_box + 8, w=65, h=25)
            os.unlink(tmp_path)
        except Exception:
            pdf.set_xy(25, y_box + 18)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*GRIS_MED)
            pdf.cell(75, 5, "[Firma digital registrada]", align="C")
    else:
        pdf.set_xy(25, y_box + 18)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*GRIS_MED)
        pdf.cell(75, 5, "[Firma digital registrada]", align="C")

    pdf.set_xy(25, y_box + 35)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*NEGRO)
    pdf.cell(75, 5, full_name, align="C")

    # Representante HogarFix
    pdf.set_xy(110, y_box + 2)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*NEGRO)
    pdf.cell(75, 5, "HOGARFIX", align="C")

    # Intentar SVG primero, luego PNG
    _img_dir = os.path.join(os.path.dirname(__file__), "..", "static", "img")
    firma_rep_svg = os.path.normpath(os.path.join(_img_dir, "firma-representante.svg"))
    firma_rep_png = os.path.normpath(os.path.join(_img_dir, "Firma R Legal.png"))

    firma_dibujada = False
    for _firma_path in (firma_rep_svg, firma_rep_png):
        if os.path.exists(_firma_path):
            try:
                pdf.image(_firma_path, x=116, y=y_box + 7, w=62, h=24)
                firma_dibujada = True
                break
            except Exception:
                continue

    if not firma_dibujada:
        # Fallback: líneas que simulan una firma
        pdf.set_draw_color(13, 13, 26)
        pdf.set_line_width(0.6)
        _fx, _fy = 120, y_box + 12
        # Crossbar T
        pdf.line(_fx, _fy + 4, _fx + 18, _fy)
        # Vertical T
        pdf.line(_fx + 9, _fy + 1, _fx + 8, _fy + 16)
        # G loop (simplificado)
        pdf.line(_fx + 24, _fy + 4, _fx + 34, _fy)
        pdf.line(_fx + 34, _fy, _fx + 38, _fy + 8)
        pdf.line(_fx + 38, _fy + 8, _fx + 30, _fy + 14)
        pdf.line(_fx + 30, _fy + 14, _fx + 24, _fy + 8)
        pdf.line(_fx + 30, _fy + 9, _fx + 38, _fy + 9)
        # Underline flourish
        pdf.set_line_width(0.4)
        pdf.line(_fx - 4, _fy + 20, _fx + 62, _fy + 18)
        pdf.set_line_width(0.3)

    pdf.set_xy(110, y_box + 31)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*NEGRO)
    pdf.cell(75, 4.5, "Tomas Garcia Guevara", align="C")
    pdf.set_xy(110, y_box + 36)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(75, 4.5, "C.C. 1029144798", align="C")
    pdf.set_xy(110, y_box + 41)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*GRIS_OSC)
    pdf.cell(75, 4.5, "Representante Legal - HogarFix", align="C")

    pdf.set_y(y_box + 52)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*NEGRO)
    pdf.field_row("Fecha de firma", fecha)
    pdf.field_row("N° Contrato", contrato_num)
    pdf.field_row("Firmado digitalmente por", f"{full_name} · {email}")
    pdf.field_row("Verificacion de identidad", _safe(
        profile.verification_status if profile else None, "pendiente").capitalize())

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*GRIS_OSC)
    pdf.multi_cell(0, 5,
        "Este documento tiene validez como contrato de prestacion de servicios de conformidad "
        "con la Ley 527 de 1999 (Comercio Electronico) y demas normas vigentes en Colombia. "
        "La firma digital registrada en la plataforma HogarFix tiene plena validez juridica.",
        align="J"
    )

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
