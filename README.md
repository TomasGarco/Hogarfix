# HogarFix MVP

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-MariaDB-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Estado](https://img.shields.io/badge/Estado-MVP%20Portafolio-059669)](./README.md)

> Marketplace web para conectar clientes con técnicos independientes en Bogotá y Cundinamarca. Reserva de servicios, gestión de perfiles, chat con IA (Fixi), contratos PDF, verificación 2FA y panel de administración.
>
> **Este repositorio es una versión MVP de prueba/portafolio. No está en producción ni conectado a pagos reales.** Ver [Roadmap](#roadmap--qué-falta-para-producción) para saber qué falta.


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
- [Manual de usuario](#manual-de-usuario)

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

> Este MVP de portafolio ya tiene las funciones principales, pero aún no es una plataforma lista para un lanzamiento productivo.
>
> A continuación se muestra todo lo que falta implementar o pulir antes de guardar y desplegar el proyecto.

---

### ❗ Qué falta en este proyecto

- Filtros de búsqueda más avanzados: precio, calificación, día disponible y tipo de servicio.
- Perfil público del técnico con URL compartible y vista sin necesidad de login.
- Panel de ingresos y historial financiero para técnicos.
- Chat directo cliente ↔ técnico asociado a cada reserva.
- Reportes administrativos con exportación (CSV / Excel) y gráficos.
- Administración de comprobantes de pago desde el panel admin.
- Pago real integrado (Wompi / PayU / pasarela de pago local).
- Verificación de identidad real para técnicos (MetaMap, Onfido, etc.).
- Notificaciones en tiempo real (WebSocket push) en todo el panel.
- Almacenamiento de archivos en la nube en lugar de disco local.
- Geolocalización de técnicos y búsqueda por distancia.
- Fotos en reseñas y portafolio del técnico con más de 3 imágenes.
- Sistema de descuentos/cupones y referidos.
- SEO básico y Open Graph para compartir en redes.
- Despliegue en servidor con Gunicorn/Nginx y HTTPS.
- Migración a PostgreSQL en producción.
- Tareas asíncronas con Celery/Redis para emails y procesos largos.

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

---

## Manual de usuario

> Guía de uso de HogarFix para: **cliente**
>
> ---

### Página principal

![Página principal de HogarFix](screenshots/Pagina%20%20Principal.png)

---

### Inicio de sesión

![Pantalla de inicio de sesión](screenshots/Inicio%20de%20sesion.png)

---

### Registro de usuario

![Formulario de registro](screenshots/Registo%20cliente.png)

---

### Panel del cliente

![Panel del cliente — Captura Cliente](screenshots/Panel%20de%20usuario.png)

---

### Panel del técnico (captura pendiente)

_No hay una captura del panel técnico en `screenshots/` aún. Añade `Panel tecnico.png` si la tienes._

---


---

### Página principal

![Página principal de HogarFix](screenshots/Pagina%20%20Principal.png)

---

### Inicio de sesión

![Pantalla de inicio de sesión](screenshots/Inicio%20de%20sesion.png)

---

### Registro de usuario

![Formulario de registro](screenshots/Registo%20cliente.png)

---

### Panel del cliente

![Panel del cliente — Captura Cliente](screenshots/Panel%20de%20usuario.png)

---




### Conceptos básicos

| Término | Qué significa en HogarFix |
|---|---|
| **Cliente** | Usuario que busca y contrata técnicos para un servicio en su hogar |
| **Técnico** | Profesional independiente que ofrece servicios (plomería, electricidad, etc.) y acepta reservas |
| **Admin** | Administrador de la plataforma. Modera usuarios, verifica técnicos y gestiona el sistema |
| **Reserva** | Solicitud de servicio que un cliente hace a un técnico para una fecha y hora específica |
| **OTP** | Contraseña de un solo uso enviada al correo para verificar el inicio de sesión (2FA) |
| **Fixi** | Chatbot de IA integrado en la plataforma. Responde preguntas sobre servicios y uso de la app |
| **Suscripción** | Plan mensual del técnico (Básico / Profesional / Elite) que define su visibilidad en la plataforma |
| **Verificación de identidad** | Proceso donde el técnico sube su cédula y una selfie para validar que es quien dice ser |
| **Comprobante de pago** | Foto del recibo o captura de pantalla de la transferencia que el cliente sube tras pagar |
| **Evidencia** | Fotos que el técnico sube al completar el trabajo (antes y después, materiales usados) |
| **Contrato PDF** | Documento legal generado automáticamente al confirmar una reserva, con datos del servicio y firma digital |
| **Badge de notificación** | Número rojo que aparece en el ícono de campana indicando notificaciones sin leer |
| **Dashboard** | Pantalla principal de cada usuario después de iniciar sesión. Resumen de actividad y accesos rápidos |

---

### Rol: Cliente

#### Cómo registrarse

1. Ir a `http://localhost:5000` → clic en **Registrarse**.
2. Completar el formulario: nombre, correo electrónico, teléfono y contraseña.
   - La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un símbolo.
3. Si está activado el OTP (2FA): revisar el correo y escribir el código de 6 dígitos que llega.
4. Listo — el sistema redirige al dashboard del cliente.

#### Cómo iniciar sesión con Google o Microsoft

- En la pantalla de login, clic en **Continuar con Google** o **Continuar con Microsoft**.
- No es necesario crear contraseña — el sistema usa la cuenta existente del proveedor.

#### Cómo buscar un técnico

1. Desde el dashboard o el menú, ir a **Buscar técnicos**.
2. Seleccionar el tipo de servicio (electricidad, plomería, etc.) y la localidad.
3. La lista muestra técnicos disponibles con foto, nombre, calificación y precio base.
4. Clic en un técnico para ver su perfil completo: portafolio de fotos, reseñas, disponibilidad.

#### Cómo hacer una reserva

1. En el perfil del técnico, clic en **Reservar servicio**.
2. Seleccionar la fecha y hora de entre los horarios disponibles del técnico.
3. Completar la dirección del servicio y una descripción del problema.
4. Elegir el método de pago (efectivo, Nequi, Daviplata, transferencia o PSE).
5. Clic en **Confirmar reserva** — el técnico recibe la solicitud.

**Estados de una reserva:**
| Estado | Qué significa |
|---|---|
| `Pendiente` | El cliente la creó, el técnico aún no ha respondido |
| `Confirmada` | El técnico aceptó. El servicio está agendado |
| `Completada` | El técnico terminó el trabajo y subió las fotos de evidencia |
| `Cancelada` | El cliente o el técnico cancelaron la reserva |

#### Cómo pagar y subir comprobante

1. Después de que el técnico complete el servicio, ir al detalle de la reserva.
2. Realizar el pago por el método acordado (fuera de la app en este MVP).
3. Clic en **Subir comprobante** → seleccionar la foto del recibo o captura de la transferencia.
4. El sistema registra el pago. El técnico puede ver el comprobante.

#### Cómo dejar una reseña

1. Cuando la reserva esté en estado `Completada`, aparece el botón **Dejar reseña**.
2. Seleccionar una calificación del 1 al 5 estrellas y escribir un comentario.
3. La reseña queda visible en el perfil público del técnico.

#### Cómo recuperar la contraseña

1. En la pantalla de login, clic en **¿Olvidaste tu contraseña?**
2. Ingresar el correo registrado → llega un enlace por email (válido por 1 hora).
3. Clic en el enlace → ingresar y confirmar la nueva contraseña.

#### Gestión de perfil y configuración

- **Perfil:** cambiar nombre, teléfono y foto de perfil.
- **Seguridad:** cerrar sesiones activas en otros dispositivos.
- **Notificaciones:** ver el historial de notificaciones (nuevas reservas, cambios de estado, etc.).
- **Configuración:** cambiar idioma (español/inglés) y preferencias de la app.

---

### Rol: Técnico

#### Cómo registrarse como técnico

El registro del técnico es en dos etapas:

**Etapa 1 — Formulario React (onboarding):**
1. Ir a `http://localhost:5000` → **Registrarse como técnico**.
2. El formulario guía paso a paso:
   - Datos personales (nombre, correo, teléfono, documento de identidad)
   - Tipo de documento y número de cédula
   - Dirección y localidades donde trabaja
   - Especialidades (electricidad, plomería, pintura, etc.)
   - Precio base por hora y tipo de cobro (fijo / por hora)
   - Días y horarios disponibles
   - Fotos de la cédula (frontal y trasera) + selfie para verificación de identidad
   - Firma digital (dibujada con el mouse o dedo en pantalla táctil)
   - Descripción de servicios y fotos de trabajos anteriores (portafolio)
3. Enviar el formulario → el sistema crea la cuenta y la pone en estado `pendiente` de verificación.

**Etapa 2 — Admin aprueba la verificación:**
- Un administrador revisa los documentos y cambia el estado a `aprobado` o `verificado`.
- El técnico recibe una notificación cuando cambia su estado.

#### Cómo iniciar sesión y ver el dashboard

- Login igual que el cliente (email/contraseña o Google/Microsoft).
- El dashboard del técnico muestra:
  - **Calendario-agenda:** mini-calendario con los días que tiene reservas marcados. Al hacer clic en un día se ven las reservas de ese día.
  - **Estadísticas:** total de reservas completadas, calificación promedio, ingresos del mes.
  - **Accesos rápidos:** confirmar reservas pendientes, gestionar disponibilidad, ver notificaciones.

#### Cómo gestionar la disponibilidad

1. Ir al menú → **Disponibilidad**.
2. Seleccionar los días de la semana en que trabaja y el horario (hora inicio → hora fin).
3. Guardar — los clientes solo podrán reservar en los horarios marcados como disponibles.

#### Cómo confirmar o rechazar una reserva

1. Cuando llega una reserva nueva, aparece el badge (número rojo) en el ícono de campana.
2. Ir a **Mis reservas** o al dashboard → ver la reserva en estado `Pendiente`.
3. Clic en **Confirmar** o **Rechazar**.
   - Al confirmar: el cliente recibe una notificación y la reserva queda agendada.
   - Al rechazar: la reserva se cancela y el cliente es notificado.

#### Cómo completar una reserva

1. Después de realizar el servicio, ir al detalle de la reserva.
2. Clic en **Completar servicio**.
3. Subir fotos de evidencia (mínimo 1, máximo las configuradas): trabajo terminado, materiales usados, estado final.
4. El sistema cambia el estado a `Completada`. El cliente puede ahora pagar y dejar reseña.

#### Cómo descargar el contrato PDF

- En el detalle de cualquier reserva confirmada, clic en **Descargar contrato**.
- El PDF se genera automáticamente con: datos del cliente, datos del técnico, fecha, hora, servicio, dirección y firma digital.

#### Suscripciones (planes)

| Plan | Qué incluye |
|---|---|
| **Básico** | Perfil visible, recibe reservas, sin prioridad en búsqueda |
| **Profesional** | Posición prioritaria en resultados de búsqueda, badge "Verificado Pro" |
| **Elite** | Máxima visibilidad, badge "Elite", hasta 5 fotos de portafolio adicionales |

- Ir a **Mi suscripción** para ver el plan actual y cambiar.
- En este MVP el cobro es sandbox (no se hace cargo real).

#### Galería de trabajos anteriores

- Ir a **Mi perfil** → sección **Portafolio**.
- Subir fotos de trabajos realizados. Aparecen en el perfil público cuando los clientes buscan técnicos.

---

### Rol: Administrador

#### Cómo acceder al panel de administración

1. Ir a `http://localhost:5000/auth/admin-access`.
2. Ingresar el código secreto de acceso (variable `ADMIN_LOGIN_CODE` del `.env`).
3. Luego hacer login normal con la cuenta admin.
4. El sistema redirige al dashboard de administración en `/admin/`.

> **Nota:** Para crear una cuenta admin se necesita el `ADMIN_REGISTER_CODE` del `.env`. No es posible registrar admins desde el formulario público.

#### Dashboard de administración

Muestra los KPIs globales de la plataforma:
- Total de usuarios (clientes + técnicos)
- Total de reservas y su distribución por estado
- Técnicos pendientes de verificación
- Reseñas recientes

#### Gestión de usuarios

- **Lista de usuarios:** buscar por nombre/correo, filtrar por rol (cliente/técnico/admin) o estado (activo/inactivo).
- **Detalle de usuario:** ver todos los datos, cambiar nombre/correo/teléfono, activar o desactivar la cuenta, eliminar el usuario.

#### Gestión de técnicos y verificación

- **Lista de técnicos:** ver todos los técnicos registrados con su estado de verificación.
- **Detalle de técnico:** ver los documentos subidos (cédula frontal, trasera, selfie), datos bio, suscripción actual.
- **Cambiar estado de verificación:**
  | Estado | Significado |
  |---|---|
  | `pending` | El técnico se registró pero el admin no ha revisado los documentos |
  | `basic_verified` | Se verificaron datos básicos (email, teléfono) |
  | `approved` | El admin aprobó el perfil — el técnico puede operar |
  | `fully_verified` | Verificación completa con documentos y antecedentes |
  | `rejected` | Los documentos no son válidos o el técnico no cumple requisitos |
- **Suspender técnico:** desactiva la cuenta temporalmente sin eliminarla.

#### Gestión de reservas y reseñas

- Ver todas las reservas de la plataforma, filtrar por estado.
- Ver todas las reseñas. Opción de moderar (eliminar) reseñas que violen los términos.

#### Anuncios modales

Los anuncios son mensajes que aparecen automáticamente al entrar a la plataforma (modal emergente).

- **Crear anuncio:** título, cuerpo del mensaje (HTML permitido), tipo (informativo / alerta / promoción), fechas de vigencia.
- **Activar/desactivar:** solo los anuncios activos se muestran a los usuarios.
- **Los usuarios pueden:** cerrar el modal y marcar "No mostrar hoy" (se guarda en localStorage y no vuelve a aparecer ese día).

---

### El chatbot Fixi

Fixi es el asistente virtual de HogarFix. Aparece como un ícono flotante en la esquina inferior derecha de todas las páginas.

**Cómo usarlo:**
1. Clic en el ícono de chat (burbuja azul).
2. Escribir la pregunta en el cuadro de texto.
3. Fixi responde en tiempo real usando IA (Groq/LLaMA) o respuestas FAQ si no hay conexión a la API.

**Qué puede responder Fixi:**
- Cómo funciona la plataforma (reservas, pagos, reseñas)
- Información sobre servicios disponibles
- Preguntas frecuentes sobre técnicos, precios y disponibilidad
- Guía de uso de la app

**Fixi no puede:**
- Ver datos de tu cuenta específica
- Hacer reservas ni pagos
- Contactar técnicos directamente

---

### Notificaciones

El sistema de notificaciones funciona así:

- El **badge** (número rojo) en el ícono de campana indica notificaciones sin leer.
- Al hacer clic en la campana se ve el historial completo de notificaciones.
- Las notificaciones se generan automáticamente por eventos como:
  - Nueva reserva recibida (técnico)
  - Reserva confirmada (cliente)
  - Reserva completada (cliente)
  - Cambio de estado de verificación (técnico)
  - Nueva reseña recibida (técnico)

> **Limitación MVP:** el badge solo se actualiza al recargar la página. Las notificaciones en tiempo real (WebSocket push) están en el roadmap.

---

### Seguridad para usuarios

- **Contraseña segura:** mínimo 8 caracteres, mayúsculas, números y símbolos.
- **OTP (2FA):** código de 6 dígitos enviado al correo en cada inicio de sesión (si está activado).
- **Alerta de login:** si inicias sesión desde un dispositivo o IP diferente, recibes un email de alerta.
- **Sesiones activas:** en Configuración puedes ver todos los dispositivos con sesión activa y cerrar los que no reconoces.
- **Recuperar contraseña:** el enlace de recuperación expira en 1 hora por seguridad.
