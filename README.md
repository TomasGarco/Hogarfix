# HogarFix MVP

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-MariaDB-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Estado](https://img.shields.io/badge/Estado-MVP%20Portafolio-059669)](./README.md)

> Marketplace web para conectar clientes con técnicos independientes en Bogotá y Cundinamarca. Reserva de servicios, gestión de perfiles, chat con IA (Fixi), contratos PDF, verificación 2FA y panel de administración.
>
> **Este repositorio es una versión MVP de prueba/portafolio. No está en producción ni conectado a pagos reales.** Ver [Roadmap](#roadmap--qué-falta-para-producción) para saber qué falta.

---

## Tabla de contenidos

- [Stack](#stack)
- [Instalación rápida](#instalación-rápida)
- [Variables de entorno (.env)](#variables-de-entorno-env)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Arquitectura](#arquitectura)
- [Base de datos](#base-de-datos)
- [Funcionalidades implementadas](#funcionalidades-implementadas)
- [Seguridad](#seguridad)
- [Configuración de servicios externos](#configuración-de-servicios-externos)
- [Solución de problemas](#solución-de-problemas)
- [Roadmap — qué falta para producción](#roadmap--qué-falta-para-producción)

---

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + Flask 3 (App Factory + Blueprints) |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Base de datos | MySQL / MariaDB (XAMPP local) |
| Frontend | HTML + Jinja2 + Bootstrap 5 local + JS vanilla |
| Frontend onboarding técnico | React + Vite + Tailwind (carpeta `frontend/`) |
| Chat en tiempo real | Flask-SocketIO (WebSocket) |
| IA chatbot Fixi | Groq API (LLaMA) + fallback FAQ local |
| Autenticación social | Authlib (Google OAuth 2.0 + Microsoft Azure) |
| Autenticación 2FA | OTP por email (HMAC-SHA256) |
| Generación PDF | fpdf2 |
| Correo | SMTP (Gmail / Mailtrap / MailerSend) |
| Seguridad | Flask-WTF (CSRF), Flask-Limiter (rate limit), bcrypt, itsdangerous |

---

## Instalación rápida

### Requisitos previos
- Python 3.11+
- XAMPP con MySQL/MariaDB corriendo en el puerto 3306

### 1. Clonar e instalar dependencias

```powershell
cd C:\xampp\htdocs\Hogarfix
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### 2. Configurar la base de datos

En phpMyAdmin (`http://localhost/phpmyadmin`):
1. Crear base de datos `hogarfix_db` con charset `utf8mb4_unicode_ci`.
2. Importar `schema.sql`.
3. Importar los parches en orden:
   - `schema_patch_payment.sql`
   - `schema_patch_evidence.sql`
   - `schema_patch_cash.sql`
   - `schema_patch_proof.sql`
   - `schema_patch_announcements.sql`

### 3. Configurar variables de entorno

```powershell
copy .env.example .env
# Editar .env con tus credenciales
```

### 4. Iniciar el servidor

```powershell
.\.venv\Scripts\Activate.ps1
py app.py
```

Abrir en el navegador: `http://localhost:5000`

> **Importante:** usar siempre `py app.py`, NO `flask run`. El proyecto usa Flask-SocketIO y requiere `socketio.run()` para que WebSocket funcione.

---

## Variables de entorno (.env)

Copiar `.env.example` a `.env` y completar los valores:

```env
# ── Seguridad ────────────────────────────────────────────────────────────────
FLASK_SECRET_KEY=clave-larga-y-aleatoria-minimo-32-caracteres
# Generar con: py -c "import secrets; print(secrets.token_hex(32))"

# ── Base de datos ─────────────────────────────────────────────────────────────
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=          # vacío en XAMPP local por defecto
MYSQL_DB=hogarfix_db

# ── Correo SMTP ───────────────────────────────────────────────────────────────
MAIL_ENABLED=true
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion_gmail
MAIL_FROM=tu_correo@gmail.com
MAIL_TIMEOUT=20

# ── IA Chatbot Fixi ───────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_...       # Sin esto Fixi usa solo respuestas FAQ locales

# ── Google OAuth (login con Google) ──────────────────────────────────────────
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback

# ── Microsoft OAuth (login con Microsoft) ────────────────────────────────────
MICROSOFT_OAUTH_CLIENT_ID=
MICROSOFT_OAUTH_CLIENT_SECRET=
MICROSOFT_OAUTH_TENANT_ID=common
MICROSOFT_OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/microsoft/callback

# ── Google Maps (geolocalización) ─────────────────────────────────────────────
GOOGLE_MAPS_API_KEY=

# ── Panel administrador ───────────────────────────────────────────────────────
ADMIN_LOGIN_CODE=codigo-secreto-para-ingresar-al-admin
ADMIN_REGISTER_CODE=codigo-secreto-para-crear-cuenta-admin

# ── OTP ───────────────────────────────────────────────────────────────────────
OTP_TTL_MINUTES=3
OTP_MAX_ATTEMPTS=3

# ── Desarrollo ────────────────────────────────────────────────────────────────
FLASK_DEBUG=false
PREFERRED_URL_SCHEME=http
SESSION_COOKIE_SECURE=false
```

---

## Estructura del proyecto

```
Hogarfix/
├── app.py                    # Punto de entrada (socketio.run)
├── config.py                 # Lee .env y configura Flask
├── schema.sql                # Script SQL completo para crear tablas
├── schema_patch_*.sql        # Parches incrementales al schema
├── requirements.txt          # Dependencias Python
├── .env.example              # Plantilla de variables de entorno
│
├── app/
│   ├── __init__.py           # create_app() — App Factory
│   ├── extensions.py         # db, login_manager, socketio, oauth, csrf, limiter
│   ├── models.py             # Tablas como clases Python (ORM)
│   ├── utils.py              # Helpers: uploads, roles, correo, alertas
│   │
│   ├── blueprints/
│   │   ├── auth.py           # /auth/   → login, registro, OTP, recuperar contraseña
│   │   ├── main.py           # /        → home, dashboard cliente, búsqueda
│   │   ├── booking.py        # /reservas/ → crear, confirmar, completar, cancelar
│   │   ├── technician.py     # /tecnico/  → dashboard, perfil, agenda, suscripción
│   │   ├── admin.py          # /admin/    → panel administrador completo
│   │   ├── chat.py           # WebSocket  → chatbot Fixi (Groq + FAQ)
│   │   └── api.py            # /api/      → endpoints JSON, webhook identidad
│   │
│   ├── services/
│   │   ├── email.py                  # Envío de correos SMTP
│   │   ├── otp.py                    # Generación/verificación de OTP
│   │   ├── contract_pdf.py           # Generación de contrato PDF
│   │   └── identity_verification.py  # Verificación de identidad (mock en MVP)
│   │
│   ├── templates/            # Plantillas Jinja2 por módulo
│   │   ├── base.html         # Base compartida (navbar, footer, scripts)
│   │   ├── base_client.html  # Base panel cliente (sidebar propio)
│   │   ├── base_tech.html    # Base panel técnico (sidebar propio)
│   │   ├── admin/            # Templates del panel administrador
│   │   ├── auth/             # Login, registro, OTP, recuperar contraseña
│   │   ├── booking/          # Crear reserva
│   │   ├── main/             # Home, dashboard, búsqueda, perfil, settings
│   │   ├── technician/       # Dashboard técnico, perfil, disponibilidad
│   │   └── errors/           # 403, 404, 500, 503
│   │
│   └── static/
│       ├── css/app.css               # Estilos globales y componentes HogarFix
│       ├── css/bootstrap.min.css     # Bootstrap 5 local
│       ├── js/                       # Bootstrap bundle, Socket.IO, helpers
│       ├── img/                      # Logos y marca
│       └── uploads/                  # Archivos subidos por usuarios
│           ├── profile/              # Fotos de perfil
│           ├── work/                 # Fotos de portafolio del técnico
│           ├── verification/         # Cédula y selfie del técnico
│           └── evidence/             # Fotos al completar una reserva
│
└── frontend/
    └── tech-registration/    # Formulario React de registro técnico (Vite + Tailwind)
```

---

## Arquitectura

```
[Navegador]  ──HTTP/WebSocket──►  [Flask (puerto 5000)]  ──SQL──►  [MySQL (puerto 3306)]
                                         │
                                   APIs externas:
                                   • Gmail SMTP  (correo)
                                   • Groq API    (IA Fixi)
                                   • Google OAuth (login social)
                                   • Microsoft OAuth (login social)
```

**Roles de usuario:**
- `cliente` → busca técnicos, reserva, paga, reseña
- `tecnico` → recibe reservas, confirma, completa con evidencia, gestiona perfil/agenda/suscripción
- `admin` → modera usuarios y técnicos, gestiona reservas/reseñas/anuncios

**Flujo de una reserva:**
```
Cliente crea reserva → Técnico confirma → Técnico completa (sube fotos evidencia)
→ Cliente sube comprobante de pago → Admin/sistema confirma pago → Cliente deja reseña
```

---

## Base de datos

**Nombre:** `hogarfix_db` | **Motor:** InnoDB | **Charset:** utf8mb4

| Tabla | Descripción |
|---|---|
| `usuarios` | Todos los usuarios: clientes, técnicos y admins. Email, contraseña (hash bcrypt), rol, nombre, teléfono, OAuth, avatar. |
| `tecnicos` | Perfil extendido del técnico. Especialidades, localidades, precio, fotos de verificación, suscripción. El campo `bio` guarda JSON con datos detallados. |
| `reservas` | Cada reserva: cliente, técnico, fecha, hora, servicio, estado, método de pago, evidencias (JSON), comprobante. |
| `disponibilidad` | Slots de agenda del técnico: fecha, hora inicio/fin, si está ocupado. |
| `resenas` | Calificación (1-5) y comentario del cliente al completar un servicio. |
| `notificaciones` | Notificaciones internas del usuario (badge en navbar). |
| `otp_verifications` | OTP temporal: hash HMAC-SHA256, sal, expiración, intentos. El código nunca se guarda en texto plano. |
| `user_sessions` | Registro de sesiones activas (token, IP, user-agent, expiración). |
| `logs_login` | Auditoría de cada inicio de sesión: IP, navegador, éxito/fallo. |
| `policy_acceptances` | Registro de aceptación de términos y condiciones. |
| `announcements` | Anuncios modales que el admin puede crear/editar/desactivar. |

**Relaciones clave:**
- `usuarios` ↔ `tecnicos` (1:1) — un técnico tiene un perfil extendido
- `usuarios` → `reservas` (1:N) — como cliente o como técnico
- `reservas` → `resenas` (1:1) — una reserva completada puede tener una reseña

---

## Funcionalidades implementadas

### Autenticación
- Registro de cliente y técnico con validación de contraseña fuerte
- Login con email/contraseña + OTP opcional por email (2FA)
- Login social con Google y Microsoft (OAuth 2.0)
- Recuperar contraseña con token firmado y expiración de 1 hora
- Múltiples sesiones con registro y cierre individual

### Panel cliente
- Dashboard con historial de reservas y estadísticas
- Búsqueda de técnicos por especialidad y localidad
- Crear reserva, ver estado, cancelar, repetir servicio
- Subir comprobante de pago (foto)
- Dejar reseña al completar un servicio
- Gestión de perfil, foto, configuración, notificaciones

### Panel técnico
- Dashboard con calendario-agenda interactivo (mini-calendario + panel de eventos del día)
- Gestión de disponibilidad (días y horarios disponibles)
- Confirmar/rechazar/completar reservas con fotos de evidencia
- Galería de fotos de trabajos anteriores
- Descarga de contrato PDF firmado digitalmente
- Sistema de suscripción: Básico / Profesional / Elite (sandbox, sin cobro real)
- Configuración, notificaciones, settings

### Panel administrador
- Dashboard con KPIs globales
- Lista de usuarios con filtros (rol, estado, búsqueda)
- Detalle de usuario: editar datos, activar/desactivar, eliminar
- Detalle de técnico: ver documentos de verificación, cambiar estado de verificación, gestionar suscripción, suspender
- Lista de reservas y reseñas con moderación
- Anuncios modales: CRUD completo (crear, editar, activar/desactivar)

### Otras funcionalidades
- **Chatbot Fixi:** IA con Groq (LLaMA) + fallback FAQ en español. WebSocket en tiempo real.
- **Contratos PDF:** generados con fpdf2, con logo, datos del técnico y firma digital.
- **Emails automáticos:** bienvenida, OTP, alerta de login desde IP nueva, recuperar contraseña.
- **Anuncios modales:** aparecen al entrar, con opción "no mostrar hoy" (localStorage).
- **Páginas legales:** términos, privacidad, política de cancelación.
- **Internacionalización:** sistema de traducciones JS (español/inglés) en settings.
- **Métodos de pago UI:** efectivo, Nequi, Daviplata, transferencia, PSE (sandbox, sin integración real).

---

## Seguridad

| Mecanismo | Implementación |
|---|---|
| Contraseñas | Hash bcrypt via Werkzeug — nunca se guarda la contraseña real |
| OTP (2FA) | HMAC-SHA256 con sal aleatoria — el código nunca se guarda en texto plano |
| Reset de contraseña | Token firmado con itsdangerous, expira en 1 hora |
| CSRF | Flask-WTF en todos los formularios |
| Rate limiting | Flask-Limiter en login, registro, OTP (máx. 5/minuto por IP) |
| Control de roles | Decorador `role_required` en todas las rutas protegidas |
| Sesiones | Flask-Login + cookie firmada con `FLASK_SECRET_KEY` |
| Auditoría | Tabla `logs_login` con IP, user-agent, éxito/fallo en cada login |
| Alerta de seguridad | Email al usuario si login desde IP o navegador diferente |
| Subida de archivos | `secure_filename` + validación de extensión + límite 10 MB |
| Credenciales | Todas en `.env`, nunca en el código fuente. `.gitignore` excluye `.env`. |
| Panel admin | Protegido con `ADMIN_LOGIN_CODE` (código secreto adicional) |

---

## Configuración de servicios externos

### Correo SMTP

El sistema soporta múltiples backends. Configurar en `.env`:

**Gmail (más simple):**
1. Activar verificación en dos pasos en Google.
2. Generar contraseña de aplicación: Google → Seguridad → Contraseñas de app.
3. Usar esa contraseña (no la real) en `MAIL_PASSWORD`.

**Mailtrap (recomendado para desarrollo/pruebas):**
- `MAIL_HOST=sandbox.smtp.mailtrap.io` | `MAIL_PORT=2525` | `MAIL_USE_TLS=true`

**Outlook / Microsoft 365:**
- `MAIL_HOST=smtp.office365.com` | `MAIL_PORT=587`

**Modo local (sin cuenta SMTP):**
- `MAIL_BACKEND=file` | `MAIL_FILE_PATH=app/mail_outbox.log`

Probar envío: `py -m flask --app app:create_app mail-test --to test@example.com`

---

### Login social (Google y Microsoft)

**Google:**
1. [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → OAuth 2.0 Client ID → Web application.
2. Redirect URI: `http://127.0.0.1:5000/auth/google/callback`
3. Copiar `client_id` y `client_secret` al `.env`.

**Microsoft:**
1. [Azure Portal](https://portal.azure.com) → App registrations → New registration.
2. Redirect URI: `http://127.0.0.1:5000/auth/microsoft/callback`
3. API permissions: `openid`, `profile`, `email`, `User.Read`.
4. Crear client secret y copiar junto con el Application ID al `.env`.

---

### Chatbot Fixi (Groq IA)

1. Crear cuenta en [console.groq.com](https://console.groq.com).
2. Generar API Key.
3. Agregar `GROQ_API_KEY=gsk_...` al `.env`.

Sin API Key, Fixi responde solo con respuestas FAQ predefinidas (funciona igual, sin IA).

---

### Verificación de identidad (modo mock en MVP)

El sistema está preparado para conectar con Onfido, Veriff o MetaMap. Actualmente usa el provider `mock` que aprueba automáticamente si se suben los 3 documentos (cédula frontal, cédula trasera, selfie).

Para activar en producción: definir `IDENTITY_PROVIDER=onfido` y `ONFIDO_API_KEY=...` en `.env`.

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `fatal: not a git repository` | No hay repo git | `git init` |
| `ModuleNotFoundError` | Entorno virtual no activo | `.\.venv\Scripts\Activate.ps1` |
| `OperationalError: Can't connect to MySQL` | MySQL de XAMPP no está corriendo | Abrir XAMPP → Start MySQL |
| `Access denied for user 'root'` | Contraseña MySQL incorrecta | Revisar `MYSQL_PASSWORD` en `.env` |
| `flask run` no soporta WebSocket | `flask run` no usa socketio | Usar `py app.py` siempre |
| OTP no llega al correo | `MAIL_ENABLED=false` o credenciales SMTP incorrectas | Revisar configuración de correo en `.env` |
| Login con Google falla | Redirect URI no coincide | Verificar URI en Google Cloud Console |
| PDF sin firma del técnico | `firma-representante-legal.png` no existe | Guardar la firma en `app/static/img/firma-representante-legal.png` |

---

## Roadmap — qué falta para producción

> Este MVP de portafolio tiene todas las funcionalidades core implementadas. Lo siguiente es lo que falta para un lanzamiento real.

---

### ✅ Lo que ya funciona

| Área | Detalle |
|---|---|
| Autenticación completa | Registro, login, OTP 2FA, recuperar contraseña, Google OAuth, Microsoft OAuth |
| Panel administrador | Dashboard, CRUD usuarios/técnicos, reservas, reseñas, anuncios, verificación, suscripciones |
| Panel técnico | Agenda-calendario, perfil, disponibilidad, suscripción, contrato PDF, notificaciones |
| Panel cliente | Dashboard, búsqueda, historial, comprobantes, reseñas, repetir servicio |
| Sistema de reservas | Crear → confirmar → completar con evidencia → reseña |
| Comprobantes de pago | Subida de foto, confirmación efectivo |
| Suscripciones técnico | Planes Básico/Profesional/Elite (sandbox) |
| Chat Fixi | Groq IA + fallback FAQ en español |
| Contratos PDF | Generación automática con firma digital |
| Emails | Bienvenida, OTP, alerta login, recuperar contraseña |
| Anuncios modales | CRUD admin, localStorage "no mostrar hoy" |
| Seguridad básica | CSRF, rate limiting, bcrypt, headers, auditoría |

---

### 🔴 Crítico — bloqueadores de producción

#### 1. Pasarela de pago real
Los métodos de pago son solo UI. No hay cobro real.
- **Solución:** Integrar **Wompi** (Bancolombia), PayU Colombia o ePlacetoPay.
- **Archivos:** `booking.py`, `technician.py` (activate_subscription), nuevo `payments.py`.

#### 2. Email al técnico al crear reserva
El técnico recibe badge interno pero no email. Si no tiene la app abierta, no se entera.
- **Solución:** En `booking.py → create_booking()`, llamar `send_email()` al técnico.
- **Archivos:** `booking.py`, `services/email.py`.

#### 3. Notificaciones push en tiempo real
El badge de notificaciones solo se actualiza al recargar la página.
- **Solución:** Emitir eventos Socket.IO en los puntos clave (nueva reserva, pago, cambio estado).
- **Archivos:** `__init__.py`, `extensions.py`, `booking.py`, templates base.

#### 4. Verificación de identidad real
El provider actual es `mock` — aprueba todo automáticamente sin verificar nada.
- **Solución:** Integrar **MetaMap**, Onfido o Veriff (MetaMap opera bien en Colombia).
- **Archivos:** `services/identity_verification.py`, variables en `.env`.

#### 5. Firma del representante legal en PDF
El archivo `app/static/img/firma-representante-legal.png` no existe. Los PDFs se generan sin firma.
- **Solución:** Guardar la firma como PNG en esa ruta.

---

### 🟡 Importante — primera semana en producción

| # | Qué falta | Archivos a modificar |
|---|---|---|
| 6 | Filtros avanzados en búsqueda (precio, rating, día disponible) | `main.py`, `templates/main/search.html` |
| 7 | Perfil público del técnico (URL compartible sin login) | Nueva ruta en `main.py`, nuevo template |
| 8 | Panel de ingresos del técnico (historial financiero) | Nueva ruta en `technician.py`, nuevo template |
| 9 | Chat directo cliente ↔ técnico por reserva | Nuevo modelo `Message`, nueva ruta, Socket.IO |
| 10 | Reportes admin (exportación + gráficas Chart.js) | Nueva ruta `admin/reports`, nuevo template |
| 11 | Gestión de comprobantes de pago en admin | `admin.py`, nuevo template `admin/pagos.html` |

---

### 🟢 Versión 2 — deseables

| # | Funcionalidad |
|---|---|
| 12 | Fotos en reseñas (hasta 3 por reseña) |
| 13 | SMS (Twilio o AWS SNS) además de email |
| 14 | Calendario exportable iCal para el técnico |
| 15 | Códigos de descuento y cupones |
| 16 | Sistema de referidos |
| 17 | Búsqueda por geolocalización (distancia al cliente) |
| 18 | Sistema de disputas/reclamaciones |
| 19 | SEO: meta description + Open Graph tags |
| 20 | Fotos en la nube (Cloudinary o Supabase Storage) en lugar de disco local |
| 21 | Despliegue en servidor (Gunicorn + Nginx en Railway, Render o VPS) |
| 22 | Migrar de MySQL a PostgreSQL para producción |
| 23 | Tareas asíncronas con Celery + Redis (emails en segundo plano) |

---

### Checklist de lanzamiento

```
ANTES DE LANZAR:
  [ ] Pasarela de pago real (Wompi / PayU)
  [ ] Email al técnico al crear reserva
  [ ] Notificaciones push en tiempo real (WebSocket)
  [ ] Verificación de identidad real (MetaMap / Onfido)
  [ ] Firma representante legal PNG
  [ ] FLASK_SECRET_KEY segura (no el valor por defecto)
  [ ] FLASK_DEBUG=false
  [ ] SESSION_COOKIE_SECURE=true (cuando sea HTTPS)

PRIMERA SEMANA EN PRODUCCIÓN:
  [ ] Filtros avanzados en búsqueda
  [ ] Perfil público del técnico
  [ ] Panel de ingresos del técnico
  [ ] Chat cliente ↔ técnico por reserva
  [ ] Reportes admin con exportación
  [ ] Vista de comprobantes en admin

VERSIÓN 2:
  [ ] Fotos en reseñas
  [ ] SMS (Twilio)
  [ ] Calendario iCal
  [ ] Códigos de descuento / referidos
  [ ] Geolocalización en búsqueda
  [ ] Sistema de disputas
  [ ] Cloudinary para fotos
  [ ] Migrar a PostgreSQL + VPS
```

---

## Comandos útiles

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
py -m pip install -r requirements.txt

# Iniciar servidor
py app.py

# Probar envío de correo
py -m flask --app app:create_app mail-test --to test@example.com

# Verificar que la app carga sin errores
py -c "from app import create_app; app=create_app(); print('OK')"

# Subir cambios al repositorio
git add .
git commit -m "descripción del cambio"
git push

# Ver qué archivos cambiaron
git status

# Ver historial de commits
git log --oneline
```

---

## Información del proyecto

- **Representante legal:** Tomas Garcia Guevara — C.C. 1029144798
- **Repositorio:** https://github.com/TomasGarco/Hogarfix
- **Dominio objetivo (producción):** hogarfix.co *(no activo en este MVP)*
- **Base de datos local:** `hogarfix_db` en `localhost:3306`
- **Puerto Flask:** `5000` → `http://localhost:5000`
