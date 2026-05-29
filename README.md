# HogarFix MVP

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-MariaDB-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Estado](https://img.shields.io/badge/Estado-MVP%20Activo-059669)](./README.md)

> Plataforma web · marketplace para conectar clientes con técnicos independientes en Bogotá y Cundinamarca. Reserva de servicios, gestión de perfiles, chat con IA (Fixi), contratos PDF, verificación 2FA y panel de administración.

---

## Capturas de pantalla

| Home | Dashboard técnico | Panel cliente |
|---|---|---|
| *(agregar `screenshots/home.png`)* | *(agregar `screenshots/dashboard-tecnico.png`)* | *(agregar `screenshots/panel-cliente.png`)* |
| Chatbot Fixi | Completar servicio | Admin |
| *(agregar `screenshots/fixi-chat.png`)* | *(agregar `screenshots/modal-completar.png`)* | *(agregar `screenshots/admin.png`)* |

> Para agregar capturas: ejecuta el proyecto (`py app.py`), toma screenshots de cada pantalla y guárdalos en una carpeta `screenshots/` en la raíz del repositorio.

---

## Tabla de contenidos

### ⚙️ Instalación y configuración
- [1. Stack y herramientas](#1-stack-y-herramientas)
- [2. Levantar el proyecto en Windows](#2-paso-a-paso-universal-para-levantar-el-proyecto-windows)
- [3. Solución de problemas comunes](#3-solución-de-problemas-comunes)
- [4. Comandos útiles](#4-comandos-útiles)
- [14. Variables .env y requirements](#14-env-y-requirements-por-que-son-importantes)
- [15. Pycache, venv y settings](#15-pycache-venv-y-settings)
- [35. Variables de entorno — detalle completo](#35-variables-de-entorno-env--qué-hace-cada-una)

### 🏗️ Arquitectura y estructura
- [5. Arquitectura monolítica](#5-arquitectura-utilizada--monolítica)
- [6. Estructura del proyecto](#6-estructura-del-proyecto-y-para-que-sirve-cada-parte)
- [19. Modelo cliente-servidor](#19-modelo-cliente-servidor--cómo-funciona-la-comunicación)
- [20. Servidor local — dirección y puertos](#20-servidor-local--dirección-puerto-dominio-e-ip)
- [21. Por qué XAMPP y phpMyAdmin](#21-por-qué-usamos-xampp-y-phpmyadmin)
- [31. Diagrama completo del proyecto](#31-arquitectura-completa-del-proyecto--diagrama)
- [43. Conceptos de arquitectura](#43-conceptos-de-arquitectura)

### 🎨 Frontend y diseño
- [7. Tipografías](#7-tipografias-usadas-y-por-que)
- [8. Paleta de colores](#8-paleta-de-colores-hex-y-rgb)
- [9. Box model y layout](#9-modelo-de-caja-box-model-y-layout)
- [10. Scripts JavaScript](#10-scripts-javascript-y-funcion)
- [30. Por qué cada tecnología](#30-lenguajes-y-tecnologías--por-qué-cada-uno)

### 🗄️ Base de datos
- [12. Base de datos relacional (MySQL)](#12-base-de-datos-relacional-mysql)
- [13. Glosario SQL rápido](#13-glosario-sql-rapido)
- [22. Base de datos — qué es y dónde se guarda](#22-base-de-datos--qué-es-dónde-se-guarda-qué-contiene)
- [25. Fotos y archivos subidos — dónde van](#25-dónde-se-guardan-las-fotos-y-archivos-subidos)
- [41. Conceptos de base de datos](#41-conceptos-de-base-de-datos-usados-en-hogarfix)

### 🔐 Seguridad y autenticación
- [11. Seguridad implementada](#11-seguridad-implementada)
- [17. Configurar correo (Mailtrap / Gmail)](#17-configurar-correo-rapido-mailtrap-o-gmail)
- [18. Login social con Google y Microsoft](#18-login-social-con-google-y-microsoft)
- [23. 2FA / OTP — cómo funciona](#23-verificación-2fa--otp--cómo-funciona-paso-a-paso)
- [24. Login con Google OAuth 2.0](#24-login-con-google-oauth-20--openid-connect)
- [29. Seguridad — resumen completo](#29-seguridad-implementada--resumen-completo)
- [42. Conceptos de seguridad](#42-conceptos-de-seguridad-usados-en-hogarfix)

### 📋 Funcionalidades principales
- [26. Chatbot Fixi — IA con Groq / LLM](#26-chatbot-fixi--ia-con-groq-no-gemini)
- [27. Generación de contrato PDF](#27-generación-de-contrato-pdf)
- [28. Sistema de correo electrónico](#28-sistema-de-correo-electrónico)
- [32. No se usa Machine Learning propio](#32-no-se-usa-machine-learning-propio)
- [33. Flujo completo de usuario — A a Z](#33-flujo-completo-de-un-usuario-nuevo--de-a-a-z)
- [34. Proceso de ejecución paso a paso](#34-proceso-de-ejecución-paso-a-paso-resumen-operativo)

### 📚 Glosario y referencia rápida
- [36. Preguntas frecuentes](#36-preguntas-frecuentes-para-presentar-el-proyecto)
- [37. Conceptos generales de programación web](#37-conceptos-generales-de-programación-web)
- [38. Archivos clave del proyecto](#38-archivos-clave-del-proyecto--qué-es-y-para-qué-sirve-cada-uno)
- [39. Librerías y servicios externos](#39-librerías-y-servicios-externos--definición-y-uso-en-hogarfix)
- [40. Credenciales y API Keys](#40-credenciales-y-api-keys--de-dónde-vienen-y-para-qué-sirven)
- [44. Términos complementarios](#44-términos-complementarios--librerías-visuales-formatos-y-protocolos)
- [45. Términos — servicios en la nube y funciones Flask](#45-términos-que-faltan--servicios-en-la-nube-funciones-flask-y-react)
- [46. ¿Habría sido más fácil con otro stack?](#46-habría-sido-más-fácil-con-otro-lenguaje-o-stack)
- [**47. Estado actual y roadmap — qué falta para producción**](#47-estado-actual-del-proyecto-y-roadmap--qué-falta-para-producción)

---

## 1. Stack y herramientas

**¿Qué es un stack?** Es el conjunto completo de tecnologías que usa una aplicación para funcionar: el lenguaje de programación, el framework web, la base de datos, el servidor, las librerías de UI y cualquier servicio externo. Se llama "stack" (pila) porque cada capa se apoya sobre la anterior — el frontend encima del backend, el backend encima de la base de datos, la base de datos encima del sistema operativo. Cuando alguien dice "el stack de HogarFix" habla de todas esas piezas juntas.

- Backend: Flask (Python)
- Arquitectura web: Flask App Factory + Blueprints
- ORM: Flask-SQLAlchemy / SQLAlchemy
- Base de datos: MySQL (MariaDB en XAMPP)
- Frontend: HTML + CSS + JavaScript
- UI: Bootstrap 5 (CDN), Bootstrap Icons, AOS (animaciones), GSAP/ScrollTrigger (home)
- Entorno: `.env` + `requirements.txt`



## 2. Paso a paso universal para levantar el proyecto (Windows)

### 2.1. Iniciar MySQL (XAMPP)    Si no sirve 
Desde XAMPP Control Panel (botón Start en MySQL) o terminal:

```powershell
cd C:\xampp\mysql\bin
.\mysqld.exe --defaults-file="C:\xampp\mysql\bin\my.ini" --console
```

Debes ver:
- `ready for connections`
- `port: 3306`

### 2.2. Preparar entorno Python y dependencias

```powershell
cd C:\xampp\htdocs\Hogarfix
# Solo la primera vez:
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### 2.3. Ejecutar el servidor

```powershell
# En la misma terminal (ya dentro del entorno virtual):
py app.py
```

Verás:
- `* Running on http://127.0.0.1:5000 (Press CTRL+C to quit)`

> **Importante:** usa siempre `py app.py`, NO `flask run`. El proyecto usa Flask-SocketIO (chat Fixi) y requiere `socketio.run()` para que WebSocket funcione correctamente. `flask run` no soporta WebSocket.

Abre en tu navegador:
- http://localhost:5000/
- http://127.0.0.1:5000/

---

## 3. Solución de problemas comunes

### Error: 'flask' no se reconoce
- Asegúrate de activar el entorno virtual antes de ejecutar cualquier comando Flask.
- Si usas varias terminales, activa el entorno en cada una.

### Error: IndentationError o problemas de mapeo SQLAlchemy
- Verifica que todos los archivos .py usen 4 espacios por nivel de indentación, nunca tabs.
- Si modificas modelos, revisa que todas las relaciones (back_populates, backref) estén bien escritas y coincidan en ambos modelos.

### Error: No module named 'pymysql' o dependencias
- Ejecuta `py -m pip install -r requirements.txt` dentro del entorno virtual.

### Error: MySQL no conecta
- Verifica que el servicio MySQL esté corriendo en XAMPP y que el puerto sea 3306.
- Si cambiaste usuario/contraseña de la base de datos, actualízalo en config.py o .env.

---

## 4. Comandos útiles

```powershell
# Activar entorno virtual (si ya existe)
cd C:\xampp\htdocs\Hogarfix
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
py -m pip install -r requirements.txt

# Ejecutar servidor
py app.py
```

---

### Recomendaciones para el desarrollo

- Siempre activa el entorno virtual antes de instalar paquetes o ejecutar Flask.
- Si tienes errores, revisa el archivo models.py y asegúrate que todas las relaciones estén bien definidas.
- Si modificas la base de datos, revisa que los modelos coincidan con el schema.sql.
- Si tienes dudas, elimina el entorno virtual y créalo de nuevo.

---


### Qué hace cada comando de terminal
- `cd ...`: cambia a la carpeta del proyecto.
- `py -m venv .venv`: crea entorno virtual local de Python.
- `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`: permite ejecutar scripts de activacion solo en esa sesion.
- `.\.venv\Scripts\Activate.ps1`: activa el entorno virtual.
- `py -m pip install -r requirements.txt`: instala dependencias exactas del proyecto.
- `$env:FLASK_APP="app.py"`: define el entrypoint para comandos Flask.
- `py -m flask init-db`: crea tablas con SQLAlchemy (`db.create_all()`).
- `py app.py`: ejecuta el servidor Flask en modo debug.
-  permite a los desarrolladores identificar y corregir errores en el código de manera eficiente.

### Si no aparece la URL del servidor al iniciar
Si no ves `Running on http://127.0.0.1:5000`, revisa esto:

1. Verificar carpeta actual:
```powershell
pwd
```
Debe ser `C:\xampp\htdocs\Hogarfix`.

2. Verificar entorno virtual activo:
- Debe verse `(.venv)` al inicio de la linea de terminal.

3. Probar con comando alternativo:
```powershell
py app.py
```

4. Si falla por puerto ocupado:
```powershell
netstat -ano | findstr :5000
```

5. Si falla por base de datos (conexion rechazada), confirma MySQL:
```powershell
C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 -P 3306 -e "SELECT VERSION();"
```

## 5. Arquitectura utilizada — Monolítica

HogarFix usa una **arquitectura monolítica modular**. Esto significa que toda la aplicación (API, lógica de negocio, vistas, autenticación, chat, etc.) vive en un único proceso Python y se despliega como una sola unidad.

Dentro del monolito, el código está organizado por módulos:
- App Factory (`create_app`) para inicializacion central.
- Blueprints por dominio de negocio (auth, booking, technician, admin, chat, api).
- Capa de modelos (SQLAlchemy) para persistencia.
- Capa de vistas (templates Jinja2 + CSS/JS).
- Utilidades comunes (subidas, roles, correo).

Esto es una arquitectura web de **3 capas** (presentación → lógica → datos), todo en un mismo proceso.

### ¿Por qué monolítica y no microservicios?
Para un MVP y equipo pequeño, el monolito es la elección correcta:
- **Más rápido de desarrollar**: no hay que gestionar comunicación entre servicios.
- **Más fácil de depurar**: todo el stack en un solo proceso y un solo log.
- **Menos infraestructura**: un servidor, una base de datos, sin orquestación.
- **Suficiente para la escala actual**: HogarFix no tiene (aún) millones de usuarios.

### ¿Se puede migrar a microservicios más adelante?
**Sí.** La estructura de Blueprints ya anticipa esa migración: cada Blueprint corresponde a un microservicio potencial.

| Blueprint actual (monolito) | Microservicio futuro equivalente |
|---|---|
| `auth.py` | Servicio de Autenticación / Identity Provider |
| `booking.py` | Servicio de Reservas |
| `technician.py` | Servicio de Técnicos / Perfiles |
| `chat.py` | Servicio de Chat en tiempo real (WebSocket) |
| `admin.py` | Servicio de Administración / Backoffice |
| `api.py` | API Gateway / BFF |

El camino de migración sería:
1. Separar cada Blueprint en su propio repositorio y proceso Python.
2. Reemplazar las llamadas directas a SQLAlchemy por llamadas HTTP entre servicios (REST o gRPC).
3. Introducir una base de datos por servicio (en lugar de la DB compartida actual).
4. Añadir un API Gateway (Nginx, Kong) que enrute el tráfico al servicio correcto.
5. Opcional: message broker (RabbitMQ, Kafka) para eventos asíncronos entre servicios.

Esto se haría de forma incremental ("strangler fig pattern"), no en un solo salto.

## 6. Estructura del proyecto y para que sirve cada parte

### Raiz del proyecto
- `app.py`: punto de entrada. Crea la app Flask y define el comando CLI `init-db`.
- `config.py`: configuracion central (DB, secretos, mail, uploads, limites).
- `schema.sql`: script SQL completo para crear la base relacional.
- `requirements.txt`: dependencias Python con versiones fijas.
- `.env.example`: plantilla de variables de entorno.
- `.vscode/settings.json`: configuracion local de VS Code (no logica de negocio).
- `.venv/`: entorno virtual de Python.
- `__pycache__/`: cache de bytecode Python (acelera imports/ejecucion).

### Carpeta `app/`
- `__init__.py`: crea app, carga config, registra blueprints y context processor.
- `extensions.py`: instancia `db` (SQLAlchemy) y `login_manager`.
- `models.py`: entidades/tablas y relaciones ORM.
- `utils.py`: helpers (roles, uploads seguros, envio de correo y alertas).

### `app/blueprints/`
- `auth.py`: registro, login, logout, recuperacion de contraseña.
- `main.py`: home, dashboard por rol, buscador de tecnicos.
- `booking.py`: creacion/estado de reservas y reseñas.
- `technician.py`: dashboard tecnico, perfil y disponibilidad.
- `admin.py`: panel admin y estados de verificacion.

### `app/templates/`
Plantillas Jinja2 por modulo (`auth`, `main`, `booking`, `technician`, `admin`) y base comun `base.html`.

### `app/static/`
- `css/app.css`: estilos globales y responsive.
- `img/`: logos, mascota e imagenes de marca.
- `uploads/`: archivos subidos por usuarios (perfil, verificacion, trabajos).

### Logo y marca (HogarFix)
Archivos principales del logo dentro de `app/static/img/`:
- `logo-hogarfix.svg`: logo principal horizontal (uso en navbar y footer).
- `logo-hogarfix-mark.svg`: isotipo compacto (favicon o usos reducidos).

Importancia:
- Mantiene identidad visual consistente en toda la plataforma.
- Mejora reconocimiento de marca en web, documentos y presentaciones.
- Permite version completa y version compacta segun el espacio disponible.

## 7. Tipografias usadas y por que
En `base.html` se cargan Google Fonts:
- Manrope: tipografia principal de lectura UI.
- Poppins: headings/marca para mas jerarquia visual.

Motivo de eleccion:
- Legibilidad alta en web/mobile.
- Buena presencia para marca y titulos.
- Compatibles con estilo moderno tipo marketplace de servicios.

## 8. Paleta de colores (hex y RGB)
Variables principales en CSS (`:root`):
- `--hf-dark`: `#0A2540` -> `rgb(10, 37, 64)`
- `--hf-cyan`: `#00D4FF` -> `rgb(0, 212, 255)`
- `--hf-orange`: `#FF6B00` -> `rgb(255, 107, 0)`
- `--hf-soft`: `#F4F8FC` -> `rgb(244, 248, 252)`

Criterio de eleccion:
- Azul oscuro: confianza/profesionalismo.
- Cian: tecnologia/soporte rapido.
- Naranja: CTA y accion (conversion).
- Fondo claro: legibilidad y contraste.

## 9. Modelo de caja (box model) y layout
Si, es necesario en este proyecto porque hay navbar responsive, cards y componentes flotantes.

Se trabaja con:
- `padding`, `margin`, `border`, `box-shadow`, `border-radius`.
- Grid/Flex de Bootstrap para estructura responsiva.
- Componentes propios (`hf-card`, `hf-navbar`, `hf-mascot-toggle`) para consistencia visual.

## 10. Scripts JavaScript y funcion

### En `base.html`
- Bootstrap Bundle: interacciones UI (collapse navbar, etc.).
- AOS: animaciones al hacer scroll.
- Script propio:
  - inicializa AOS,
  - controla boton flotante de mascota (abrir/cerrar panel de ayuda).

### En `auth/register.html`
- Validacion en vivo de telefono por pais.
- Validacion de fortaleza de contraseña.
- Validacion final de formulario antes de enviar.

### En `main/home.html`
- GSAP + ScrollTrigger para animaciones de entrada/scroll en home.

## 11. Seguridad implementada
- Passwords con hash (`generate_password_hash` / `check_password_hash`).
- Control de acceso por rol con decorador `role_required`.
- Sesion con Flask-Login.
- Validacion de contraseña fuerte en registro/reset.
- Tokens temporales para recuperacion de contraseña (`itsdangerous`).
- Registro de logins (`logs_login`) con IP y user-agent.
- Alerta de email ante login inusual (cambio de IP o user-agent).
- Subidas de archivos con extension permitida y nombre saneado (`secure_filename`).

## 12. Base de datos relacional (MySQL)
Motor: InnoDB

Tablas principales:
- `usuarios`: credenciales, rol, estado.
- `tecnicos`: perfil tecnico y verificacion.
- `reservas`: servicios reservados (cliente-tecnico).
- `disponibilidad`: slots de agenda del tecnico.
- `resenas`: calificacion por servicio confirmado.
- `logs_login`: auditoria de inicios de sesion.

Relaciones importantes:
- Un usuario tecnico -> un perfil tecnico (1:1).
- Un cliente y un tecnico -> muchas reservas (1:N + 1:N).
- Una reserva -> maximo una reseña (1:1).

## 13. Glosario SQL rapido
- `NULL`: valor ausente/desconocido.
- `NOT NULL`: campo obligatorio.
- `TEXT`: texto largo.
- `VARCHAR(n)`: texto corto hasta `n` caracteres.
- `INT`: numero entero.
- `TINYINT`: entero pequeño (en MySQL se usa mucho como booleano 0/1).
- `TINYINT(1)`: convencion visual para booleano (`0` falso, `1` verdadero).
- `UNSIGNED`: no acepta negativos.
- `AUTO_INCREMENT`: incremento automatico para ID.
- `PRIMARY KEY`: identificador unico de la fila.
- `FOREIGN KEY`: referencia entre tablas.
- `UNIQUE`: impide duplicados.
- `DEFAULT`: valor por defecto.
- `ON DELETE CASCADE`: si borras padre, borra hijos.
- `ON DELETE SET NULL`: al borrar padre, deja referencia en NULL.
- `ON UPDATE CASCADE`: si cambia clave padre, actualiza hijos.

## 14. .env y requirements por que son importantes
- `.env`: centraliza configuracion sensible (secretos, host, credenciales, puertos) sin hardcodear.
- `requirements.txt`: asegura que todos instalen exactamente las mismas versiones.

## 15. Pycache, venv y settings
- `__pycache__`: mejora rendimiento; Python guarda bytecode
- lenguaje de bajo nivel, abstracto y compacto, generado al compilar código fuente

-  `.pyc` para no recompilar siempre.
- `.venv`: entorno aislado para dependencias del proyecto (evita conflictos globales).
- `.vscode/settings.json`: define preferencias del workspace en VS Code (por ejemplo, entorno Python por defecto).

## 16. Mensajes de consola del navegador (los que viste)
- `[Intervention] Images loaded lazily...`: informativo del navegador, no error de tu app.
- `Tracking Prevention blocked access to storage`: politica de privacidad del navegador, no rompe Flask.
- `404 /favicon.ico`: faltaba favicon por ruta default del navegador; se corrige declarando icono en `base.html`.

## 17. Configurar correo rapido (Mailtrap o Gmail)

Si ves el mensaje "El correo esta desactivado en el servidor", significa que `MAIL_ENABLED` esta en `false` o faltan credenciales SMTP.

### 17.0 Sin cuenta externa (modo local recomendado para desarrollo)
Si no tienes cuenta en Mailtrap, MailerSend, Gmail u Outlook, puedes simular envio guardando correos en archivo local.

Configura en `.env`:
1. `MAIL_ENABLED=true`
2. `MAIL_BACKEND=file`
3. `MAIL_FILE_PATH=app/mail_outbox.log`

Prueba envio:
1. `py -m flask --app app:create_app mail-test --to test@example.com`

## 18. Login social con Google y Microsoft

La implementacion de este proyecto usa Flask + Authlib sobre el login actual. No se usa Node.js en este repositorio.

### Variables necesarias
Configura estas variables en tu `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=tu_client_id_google
GOOGLE_OAUTH_CLIENT_SECRET=tu_client_secret_google
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback

MICROSOFT_OAUTH_CLIENT_ID=tu_client_id_microsoft
MICROSOFT_OAUTH_CLIENT_SECRET=tu_client_secret_microsoft
MICROSOFT_OAUTH_TENANT_ID=common
MICROSOFT_OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/microsoft/callback

SESSION_COOKIE_SECURE=false
PREFERRED_URL_SCHEME=http
```

### Google Cloud Console
1. Crea un proyecto en Google Cloud.
2. Activa Google Identity Services.
3. Crea credenciales OAuth 2.0 tipo Web application.
4. Agrega como redirect URI: `http://127.0.0.1:5000/auth/google/callback`
5. Copia client ID y client secret al `.env`.

### Microsoft Azure Portal
1. Entra a Azure Portal > App registrations > New registration.
2. Usa tenant `common` si quieres cuentas personales y de organizacion.
3. Agrega como redirect URI Web: `http://127.0.0.1:5000/auth/microsoft/callback`
4. Crea un client secret.
5. Copia Application (client) ID y secret al `.env`.
6. En API permissions agrega `openid`, `profile`, `email` y `User.Read`.

### Flujo implementado
1. El usuario pulsa `Continuar con Google` o `Continuar con Microsoft`.
2. Flask redirige al proveedor con OAuth 2.0 / OpenID Connect.
3. El proveedor devuelve el token al callback.
4. El backend valida el token y obtiene nombre, email y avatar opcional.
5. Si el usuario no existe se crea como `cliente`.
6. Si ya existe, se inicia sesion con cookie segura de Flask-Login.

### Seguridad
1. El estado OAuth protege contra CSRF.
2. Se valida el `id_token` usando el proveedor OpenID.
3. En produccion debes usar `https` y `SESSION_COOKIE_SECURE=true`.
4. Las cuentas admin siguen excluidas del login social por seguridad.

Resultado:
1. El sistema devuelve "Correo de prueba enviado correctamente".
2. El contenido del correo queda en `app/mail_outbox.log`.

### 17.1 Mailtrap (recomendado para pruebas)
1. Crea una cuenta en Mailtrap y abre tu Inbox de prueba.
2. Copia credenciales SMTP (host, puerto, username, password).
3. Crea `.env` tomando como base `.env.example`.
4. Completa estos valores en `.env`:
  - `MAIL_ENABLED=true`
  - `MAIL_HOST=sandbox.smtp.mailtrap.io`
  - `MAIL_PORT=2525`
  - `MAIL_USE_TLS=true`
  - `MAIL_USE_SSL=false`
  - `MAIL_USERNAME=...`
  - `MAIL_PASSWORD=...`
  - `MAIL_FROM=no-reply@hogarfix.co`

Prueba envio:
1. `py -m flask --app app:create_app mail-test --to tu_correo@dominio.com`
2. Revisa el inbox de Mailtrap.

### 17.2 Gmail (produccion simple)
1. Activa verificacion en dos pasos en Google.
2. Genera una clave de aplicacion.
3. Configura en `.env`:
  - `MAIL_ENABLED=true`
  - `MAIL_HOST=smtp.gmail.com`
  - `MAIL_PORT=587`
  - `MAIL_USE_TLS=true`
  - `MAIL_USE_SSL=false`
  - `MAIL_USERNAME=tu_correo@gmail.com`
  - `MAIL_PASSWORD=tu_clave_de_aplicacion`
  - `MAIL_FROM=tu_correo@gmail.com`

Prueba envio:
1. `py -m flask --app app:create_app mail-test --to tu_correo@dominio.com`

### 17.3 Outlook / Microsoft 365
Configura en `.env`:
  - `MAIL_ENABLED=true`
  - `MAIL_HOST=smtp.office365.com`
  - `MAIL_PORT=587`
  - `MAIL_USE_TLS=true`
  - `MAIL_USE_SSL=false`
  - `MAIL_USERNAME=tu_correo@outlook.com`
  - `MAIL_PASSWORD=tu_password_o_app_password`
  - `MAIL_FROM=tu_correo@outlook.com`

Prueba envio:
1. `py -m flask --app app:create_app mail-test --to tu_correo@dominio.com`

Notas para Outlook:
1. Si tienes MFA (doble factor), usa App Password.
2. Si es cuenta corporativa Microsoft 365, el admin puede bloquear SMTP AUTH.
3. Si falla con `mail-error`, valida que SMTP AUTH este habilitado en la cuenta.

### 17.4 MailerSend con API token (recomendado si SMTP falla)
Configura en `.env`:
1. `MAIL_ENABLED=true`
2. `MAIL_BACKEND=api`
3. `MAIL_API_TOKEN=tu_token_api_mailersend`
4. `MAIL_API_URL=https://api.mailersend.com/v1/email`
5. `MAIL_FROM=tu_sender_verificado@tu-dominio.com`
6. `MAIL_FROM_NAME=HogarFix`

Prueba envio:
1. `py -m flask --app app:create_app mail-test --to tu_correo@dominio.com`

Notas:
1. El `MAIL_FROM` debe ser un remitente verificado en MailerSend.
2. Si el token no tiene permisos de envio, devolvera error de API.

## Notas finales de la guía de configuración
- Si MySQL usa contraseña, define `MYSQL_PASSWORD` en `.env`.
- Si cambias puerto MySQL, ajusta `MYSQL_PORT`.
- Si cambias puerto Flask, actualiza la URL de acceso.
- Este MVP no incluye pagos ni chat en tiempo real por diseño.

---

# GUIA TECNICA COMPLETA — HOGARFIX
> Esta sección explica cada componente del proyecto en profundidad: cómo funciona, quién lo ejecuta, dónde se guarda cada cosa, y por qué se tomaron estas decisiones. Pensada para que cualquier persona pueda entender y presentar el proyecto.

---

## 19. Modelo cliente-servidor — cómo funciona la comunicación

HogarFix usa el modelo clásico **cliente-servidor**:

```
[Navegador del usuario]  ←HTTP/WebSocket→  [Servidor Flask]  ←SQL→  [MySQL]
       (cliente)                               (servidor)            (base de datos)
```

- **Cliente**: el navegador (Chrome, Firefox, etc.). Pide páginas, envía formularios y se comunica con el servidor por HTTP y WebSocket.
- **Servidor**: Python/Flask corriendo en la misma máquina (por ahora local). Recibe las peticiones, aplica la lógica de negocio, consulta la base de datos y responde con HTML o JSON.
- **Base de datos**: MySQL, corriendo también local gracias a XAMPP. Solo el servidor habla con ella; el navegador nunca toca la DB directamente.

Esto es una arquitectura de **3 capas** (presentación → lógica → datos), todo corriendo en local en este momento.

---

## 20. Servidor local — dirección, puerto, dominio e IP

| Concepto | Valor actual (desarrollo local) |
|---|---|
| Dirección IP local | `127.0.0.1` |
| Alias de localhost | `localhost` |
| Puerto Flask | `5000` |
| URL completa | `http://localhost:5000` o `http://127.0.0.1:5000` |
| Puerto MySQL | `3306` |
| Dominio real (producción) | `hogarfix.co` (no activo aún en este MVP) |

**¿Por qué el puerto 5000?**
Flask usa el puerto 5000 por convención en desarrollo. Es un puerto no privilegiado (por encima del 1024) que no requiere permisos de administrador para abrir. En producción se usaría el puerto 80 (HTTP) o 443 (HTTPS) detrás de un servidor como Nginx o Apache.

**¿Por qué `127.0.0.1` y no una IP de red?**
`127.0.0.1` es la interfaz de loopback: solo el propio equipo puede acceder. Esto es intencional en desarrollo para no exponer el servidor a la red local. Si quieres que otros en la misma red lo vean, debes iniciar Flask con `--host=0.0.0.0`.

**¿Por qué NO se usa el puerto 1500?**
El proyecto no usa el puerto 1500 en ningún componente actual. Flask usa 5000 y MySQL usa 3306. Si en algún momento viste el 1500, posiblemente era otro servicio ajeno al proyecto.

---

## 21. Por qué usamos XAMPP y phpMyAdmin

**XAMPP** es un paquete gratuito que instala en un solo clic:
- Apache (servidor web, no lo usamos directamente pero viene incluido)
- **MySQL / MariaDB** — la base de datos que SÍ usamos
- **phpMyAdmin** — interfaz web para ver y administrar MySQL

**¿Por qué XAMPP y no instalar MySQL solo?**
- Es la forma más rápida de tener MySQL funcionando en Windows sin configuración manual.
- phpMyAdmin permite ver las tablas, ejecutar SQL, importar el `schema.sql` y revisar datos, todo desde el navegador sin escribir comandos.
- Es estándar educativo y en proyectos freelance/startup en Latinoamérica.

**¿Por qué phpMyAdmin?**
- Permite importar el archivo `schema.sql` con un clic para crear todas las tablas.
- Permite ver qué hay en la base de datos en tiempo real mientras se prueba la app.
- Corre en `http://localhost/phpmyadmin` una vez que MySQL está activo en XAMPP.

**Flask NO depende de Apache de XAMPP.** Flask tiene su propio servidor web integrado (Werkzeug / eventlet). XAMPP solo se usa para arrancar MySQL.

---

## 22. Base de datos — qué es, dónde se guarda, qué contiene

### Motor y nombre
- **Motor**: MySQL (MariaDB en XAMPP)
- **Base de datos**: `hogarfix_db`
- **Codificación**: `utf8mb4` (soporta emojis y caracteres especiales del español)
- **Host**: `localhost` / `127.0.0.1`
- **Puerto**: `3306`
- **Usuario**: `root` (sin contraseña en XAMPP local por defecto)

### ¿Dónde se guardan físicamente los datos?
Los archivos de la base de datos se guardan en el disco duro del equipo donde corre XAMPP:
```
C:\xampp\mysql\data\hogarfix_db\
```
Son archivos binarios (`.ibd`, `.frm`) que MySQL gestiona internamente. No los edites a mano.

### ¿Cómo se conecta Flask a MySQL?
La cadena de conexión se arma en `config.py`:
```
mysql+pymysql://root:@localhost:3306/hogarfix_db
```
- `mysql+pymysql`: driver (PyMySQL, instalado en `requirements.txt`)
- `root:`: usuario `root` sin contraseña
- `localhost:3306`: host y puerto
- `hogarfix_db`: nombre de la base de datos

Flask-SQLAlchemy usa esta URL para abrir una conexión al arrancar y mantener un pool de conexiones reutilizables.

### Tablas de la base de datos y para qué sirven

| Tabla | Para qué sirve |
|---|---|
| `usuarios` | Todos los usuarios: clientes, técnicos y admins. Email, contraseña (hash), rol, nombre, teléfono, dirección, OAuth, avatar. |
| `tecnicos` | Perfil ampliado del técnico: foto, especialidades, localidades, precio, fotos de verificación de identidad, estado de verificación. |
| `reservas` | Cada reserva de servicio: quién reservó (cliente), a quién (técnico), fecha, hora, servicio, estado, método de pago, evidencias. |
| `disponibilidad` | Slots de agenda del técnico: días de la semana, hora inicio/fin, excepciones de días. |
| `resenas` | Calificación (1-5) y comentario que el cliente deja después de un servicio completado. |
| `otp_verifications` | Código OTP temporal: hash del código, sal criptográfica, expiración, intentos. |
| `user_sessions` | Registro de sesiones activas: token, IP, user-agent, expiración. |
| `logs_login` | Auditoría de inicios de sesión: IP, navegador, éxito/fallo, fecha. |
| `notificaciones` | Notificaciones internas del usuario en la plataforma. |
| `policy_acceptances` | Registro de aceptación de términos y condiciones. |

### ¿Cómo se crean las tablas?
Importando `schema.sql` en phpMyAdmin o ejecutando:
```powershell
C:\xampp\mysql\bin\mysql.exe -u root hogarfix_db < schema.sql
```

---

## 23. Verificación 2FA / OTP — cómo funciona paso a paso

### ¿Qué es OTP?
OTP significa **One-Time Password** (contraseña de un solo uso). Es el código de 6 dígitos que llega al correo y sirve para confirmar que eres tú quien está iniciando sesión o registrándose.

### ¿Qué tipo de 2FA usa HogarFix?
HogarFix usa **OTP por correo electrónico**, NO una app de autenticación (TOTP). Esto significa:
- Se genera un código aleatorio de 6 dígitos.
- Se envía al correo registrado del usuario.
- El usuario lo ingresa en la plataforma.
- Si es correcto y no expiró, continúa.

### Flujo completo paso a paso

```
1. Usuario inicia sesión con email + contraseña.
2. Flask verifica la contraseña (hash bcrypt).
3. Si el usuario tiene 2FA activo → genera OTP.
4. Flask llama a issue_otp_for_user():
   a. Genera código de 6 dígitos con secrets.randbelow() (criptográficamente seguro).
   b. Genera una "sal" aleatoria de 32 caracteres.
   c. Aplica HMAC-SHA256(sal + código) para obtener el hash.
   d. Guarda en la tabla otp_verifications: hash, sal, expiración (3 min), intentos máximos.
   e. El código en texto plano NUNCA se guarda en DB.
5. Flask llama a send_otp_code_email() → correo con el código al usuario.
6. Usuario ve pantalla de verificación, ingresa el código.
7. Flask recupera el registro OTP de la DB, rehace el HMAC y compara.
8. Si coincide y no expiró → sesión iniciada, OTP eliminado.
9. Si falla 3 veces → OTP bloqueado, debe pedir nuevo código.
```

### ¿Dónde se guarda el código OTP?
- **En la DB (`otp_verifications`)**: solo el **hash** del código, nunca el código real.
- **En el correo del usuario**: el código en texto plano (solo válido por 3 minutos).
- **Google NO guarda nada** del OTP. Google solo interviene si el usuario usa "Iniciar sesión con Google" (OAuth, explicado abajo).

### ¿Quién genera el OTP?
El servidor Flask, específicamente el archivo `app/services/otp.py`, función `issue_otp_for_user()`.

### ¿Quién envía el correo con el OTP?
El servidor Flask usando SMTP (Gmail), desde `app/utils.py` → función `send_otp_code_email()`. El correo sale de la cuenta `tmtomas62@gmail.com` con una contraseña de aplicación de Google (no la contraseña real de Gmail).

### Configuración OTP en `.env`
```env
OTP_TTL_MINUTES=3          # El código expira en 3 minutos
OTP_MAX_ATTEMPTS=3         # Máximo 3 intentos antes de bloquear
```

---

## 24. Login con Google (OAuth 2.0 / OpenID Connect)

### ¿Qué es y por qué se implementó?
Permite al usuario iniciar sesión con su cuenta de Google sin necesidad de crear una contraseña nueva en HogarFix. Es más cómodo y más seguro porque Google gestiona la contraseña del usuario.

### ¿Qué guarda Google?
Google guarda:
- Las credenciales del usuario (su contraseña de Google, verificación en 2 pasos de Google).
- El hecho de que la app HogarFix tiene autorización de ese usuario.

Google **NO guarda** reservas, perfiles técnicos, ni datos de negocio de HogarFix.

### ¿Qué guarda HogarFix de Google?
Solo:
- El `email` del usuario (para identificarlo).
- El `oauth_subject` (ID único de Google para ese usuario, no es la contraseña).
- El `oauth_provider` (valor `"google"`).
- El `avatar_url` (foto de perfil de Google, opcional).

Nada más. La contraseña de Google nunca llega al servidor de HogarFix.

### Flujo OAuth paso a paso

```
1. Usuario pulsa "Continuar con Google".
2. Flask genera un "state" aleatorio (protección CSRF) y redirige a Google.
3. Google muestra su pantalla de autenticación.
4. Usuario autoriza HogarFix en Google.
5. Google redirige al callback: /auth/google/callback?code=...&state=...
6. Flask valida el "state" (anti-CSRF) y solicita el token a Google.
7. Flask obtiene el id_token con email, nombre y foto.
8. Flask busca en DB si ya existe ese email/oauth_subject.
9. Si no existe → crea cuenta nueva como "cliente".
10. Si existe → inicia sesión directamente.
11. Sesión manejada por Flask-Login con cookie segura.
```

### ¿Quién implementa OAuth en el código?
La librería `Authlib` (instalada en `requirements.txt`), configurada en `app/extensions.py` y `app/__init__.py`. El blueprint `app/blueprints/auth.py` maneja las rutas `/auth/google/callback` y `/auth/google`.

### ¿Dónde se configura?
En Google Cloud Console:
1. Proyecto → APIs & Services → Credentials → OAuth 2.0 Client IDs.
2. Tipo: Web application.
3. Redirect URI: `http://127.0.0.1:5000/auth/google/callback`
4. Se obtiene `client_id` y `client_secret` que van al `.env`.

---

## 25. Dónde se guardan las fotos y archivos subidos

### Ubicación en disco

```
C:\xampp\htdocs\Hogarfix\app\static\uploads\
    profile\       ← fotos de perfil (clientes y técnicos)
    verification\  ← documentos de identidad del técnico (cédula frontal, trasera, selfie)
    work\          ← fotos de trabajos anteriores del técnico (galería de portafolio)
    evidence\      ← fotos antes/después subidas al completar una reserva
```

### ¿Qué datos guarda cada rol?

| Tipo de dato | ¿Quién lo genera? | Carpeta en disco | Columna en DB |
|---|---|---|---|
| Foto de perfil | Cliente o técnico | `uploads/profile/` | `usuarios.avatar_url` / `tecnicos.profile_photo` |
| Foto de portafolio (trabajos anteriores) | Técnico | `uploads/work/` | `tecnicos.bio` → campo `work_photos` (JSON) |
| Cédula / documento de identidad | Técnico (onboarding) | `uploads/verification/` | `tecnicos.bio` → campo `id_doc_*` |
| Selfie de verificación | Técnico (onboarding) | `uploads/verification/` | `tecnicos.bio` → campo `selfie` |
| Fotos antes/después de servicio | Técnico (al completar reserva) | `uploads/evidence/` | `reservas.evidence_photos` (JSON con rutas) |

### ¿Quién guarda los archivos?
El servidor Flask, en la función `save_upload()` de `app/utils.py`. Cuando el usuario sube una imagen desde el formulario:
1. Flask recibe el archivo en memoria.
2. Valida la extensión (solo `jpg`, `jpeg`, `png`, `gif`, `webp`, `pdf`).
3. Genera un nombre seguro con `secure_filename()` (evita path traversal).
4. Guarda el archivo físico en la carpeta correspondiente.
5. Guarda la ruta relativa en la base de datos (columna `profile_photo`, `avatar_url`, etc.).

### ¿Cómo se sirven al navegador?
Flask sirve los archivos desde `/static/uploads/...` automáticamente. La URL resultante es:
```
http://localhost:5000/static/uploads/profile/nombre-archivo.jpg
```

### Límite de tamaño
Configurado en `config.py`: máximo **10 MB** por archivo (`MAX_CONTENT_LENGTH = 10 * 1024 * 1024`).

### ¿Se usan servicios en la nube para las fotos?
En el MVP actual, **no**. Todo se guarda en disco local. El frontend React (`frontend/tech-registration/`) tiene código preparado para Cloudinary (servicio de almacenamiento en la nube), pero eso es para una versión futura. Hoy todo queda en `app/static/uploads/`.

---

## 26. Chatbot Fixi — IA con Groq (no Gemini)

### ¿Qué es Fixi?
Fixi es el asistente virtual de HogarFix. Aparece como un botón flotante en la plataforma y responde preguntas sobre cómo usar la app, reservas, técnicos, etc.

### ¿Qué es un LLM (Modelo de Lenguaje Grande)?
**LLM** son las siglas de *Large Language Model* (Modelo de Lenguaje Grande). Es un tipo de inteligencia artificial entrenada con enormes cantidades de texto para entender y generar lenguaje humano de forma coherente.

Cómo funciona de forma simple:
```
1. Se alimenta al modelo con miles de millones de textos (libros, webs, código, etc.).
2. El modelo aprende patrones estadísticos: qué palabras tienden a seguir a otras.
3. Cuando le haces una pregunta, predice cuál es la respuesta más probable
   palabra por palabra, en milisegundos.
4. El resultado parece una respuesta inteligente porque el modelo aprendió
   cómo responden los humanos a ese tipo de preguntas.
```

Ejemplos de LLMs conocidos:
| Empresa | LLM | Acceso |
|---|---|---|
| OpenAI | GPT-4, GPT-4o | API de pago |
| Google | Gemini | API de pago / gratuito |
| Meta | LLaMA 3 | Código abierto |
| Anthropic | Claude | API de pago |
| Groq | sirve varios (LLaMA, Mixtral…) | API rápida |

Lo que hace **único a Groq** no es que haya creado un LLM propio, sino que tiene hardware especializado (LPU — *Language Processing Unit*) que ejecuta los LLMs existentes (como LLaMA de Meta) a velocidades mucho más altas que una GPU convencional.

### ¿Qué IA usa? (IMPORTANTE: es Groq, no Gemini)
El chatbot usa la API de **Groq** (no Google Gemini). Groq es un servicio de IA que ejecuta LLMs de terceros (como LLaMA de Meta) con velocidad muy alta. El modelo específico depende de lo que esté disponible en la cuenta de Groq configurada.

### ¿Cómo funciona?
```
1. Usuario escribe un mensaje en el chat de Fixi.
2. El navegador envía el mensaje al servidor Flask por WebSocket (Socket.IO).
3. Flask recibe el mensaje en app/blueprints/chat.py.
4. Flask consulta primero la base de conocimiento local (FAQ hardcodeada).
5. Si ninguna palabra clave del FAQ coincide → llama a la API de Groq.
6. Groq responde con texto generado por IA.
7. Flask envía la respuesta de vuelta al navegador por WebSocket.
8. El chat muestra la respuesta en tiempo real.
```

### Fallback FAQ local
Si Groq no está configurado (sin API key) o falla, Fixi responde con respuestas predefinidas basadas en palabras clave (registro, reserva, precio, técnico, contraseña, etc.). Esto asegura que el chat siempre funcione aunque no haya conexión con Groq.

### ¿Quién gestiona la comunicación en tiempo real?
**Flask-SocketIO** (instalado en `requirements.txt`), que implementa el protocolo WebSocket. Por eso el proyecto se inicia con `py app.py` (que usa `socketio.run()`) y NO con `flask run` (que no soporta WebSocket).

### Configuración en `.env`
```env
GROQ_API_KEY=tu_api_key_de_groq
```
Sin esta variable, Fixi funciona solo con respuestas FAQ locales.

### ¿Usa Machine Learning propio?
**No.** HogarFix no entrena ningún modelo de ML. Solo consume la API de Groq, que ya tiene modelos pre-entrenados. No hay scikit-learn, TensorFlow, PyTorch ni ningún framework de ML en el proyecto.

---

## 27. Generación de contrato PDF

### ¿Qué es?
Al completar el proceso de onboarding, el técnico puede descargar un contrato de prestación de servicios en PDF firmado digitalmente.

### ¿Quién lo genera?
El servidor Flask, usando la librería `fpdf2` (instalada en `requirements.txt`). El archivo `app/services/contract_pdf.py` contiene la clase `ContratoHogarFix`.

### ¿Qué contiene el PDF?
- Logo de HogarFix en el encabezado.
- Datos del técnico (nombre, documento, especialidades).
- Datos del representante legal: **Tomas Garcia Guevara, C.C. 1029144798**.
- Firma digital del representante (imagen PNG desde `app/static/img/firma-representante-legal.png`).
- Firma digital del técnico (imagen base64 capturada con el pad de firma del formulario de registro).
- Fecha y lugar (Bogotá, Colombia).

### ¿Dónde se genera?
En memoria del servidor (`BytesIO`), no en disco. Se envía directamente al navegador como descarga sin guardar el PDF en el servidor.

---

## 28. Sistema de correo electrónico

### ¿Cómo se envían los correos?
Usando **SMTP** directamente desde Python (sin librerías externas de Flask para mail). El módulo `app/utils.py` contiene `_send_via_smtp()`.

### Correos que envía la plataforma
| Evento | Correo enviado |
|---|---|
| Registro exitoso | Bienvenida con logo Fixi inline |
| Inicio de sesión | OTP de 6 dígitos para verificación |
| Login desde IP nueva | Alerta de seguridad |
| Recuperar contraseña | Enlace temporal con token firmado |

### ¿Quién envía los correos?
La cuenta de Gmail `tmtomas62@gmail.com` con una contraseña de aplicación (no la contraseña real). Google genera contraseñas de aplicación para apps de terceros que no soportan OAuth.

### ¿Por qué Gmail y no un servicio de email profesional?
Para el MVP local es suficiente. En producción se recomendaría migrar a SendGrid, MailerSend o Amazon SES para mayor entregabilidad y reputación del remitente.

### Estructura técnica del correo
Los correos HTML con logo usan formato MIME `multipart/related`:
```
Email MIME
  └── multipart/related
        ├── multipart/alternative
        │     ├── text/plain (fallback)
        │     └── text/html (correo visual)
        └── image/png (logo Fixi embebido por CID)
```
El logo aparece inline en el correo sin depender de una URL externa.

---

## 29. Seguridad implementada — resumen completo

| Mecanismo | Dónde | Para qué |
|---|---|---|
| Hash de contraseñas (bcrypt) | `models.py` `set_password()` | Nunca se guarda la contraseña real |
| OTP HMAC-SHA256 | `services/otp.py` | El código OTP nunca se guarda en texto plano |
| Token de reset firmado | `auth.py` `itsdangerous` | El enlace de recuperación expira y no puede falsificarse |
| CSRF Protection | `Flask-WTF` en todos los forms | Evita ataques desde sitios externos |
| Rate Limiting | `Flask-Limiter` por ruta | Bloquea intentos de fuerza bruta |
| Control de roles | `role_required` en blueprints | Cliente no puede ver panel técnico y viceversa |
| Sesiones seguras | Flask-Login + cookie firmada | No se puede falsificar una sesión |
| Auditoría de logins | Tabla `logs_login` | Registro de cada intento con IP y navegador |
| Alerta de login inusual | `send_login_alert_email` | Avisa al usuario si inicia sesión desde IP nueva |
| Subidas seguras | `secure_filename` + validación de extensión | Evita subir archivos ejecutables o rutas maliciosas |
| Nombres de archivos en DB, no rutas absolutas | `utils.py` | Evita path traversal |
| Variables sensibles en `.env` | `config.py` + `python-dotenv` | Las credenciales no van al código fuente |
| Verificación de identidad técnicos | `services/identity_verification.py` | Antes de activar perfil técnico se verifican documentos |
| Suspensión de técnicos | `tecnicos.suspension_type` | Admin puede suspender temporal o definitivamente |
| Código de acceso admin | `ADMIN_LOGIN_CODE` en `.env` | El panel admin solo accesible con código secreto |

---

## 30. Lenguajes y tecnologías — por qué cada uno

### Python / Flask
- **¿Por qué Python?** Ecosistema enorme para web, fácil de leer, amplia comunidad en Latinoamérica, y excelente para integrar APIs de IA (Groq).
- **¿Por qué Flask y no Django?** Flask es micro-framework: más ligero, más control, mejor para MVP. Django tiene más convenciones que pueden ser exceso para este tamaño de proyecto.
- **¿Por qué Flask App Factory + Blueprints?** Permite escalar el proyecto sin que todo esté en un solo archivo. Cada dominio (auth, booking, técnico, admin) tiene su propio blueprint.

### MySQL / MariaDB
- **¿Por qué SQL y no NoSQL (MongoDB)?** Los datos de HogarFix son relacionales: un usuario tiene un perfil técnico, un técnico tiene reservas, una reserva tiene reseña. Las relaciones son lo más importante. MySQL las maneja perfectamente con claves foráneas.
- **¿Por qué SQLAlchemy y no SQL directo?** ORM: escribe Python y él genera el SQL. Más seguro (previene SQL injection automáticamente), más mantenible.

### HTML + Jinja2
- **¿Por qué Jinja2?** Es el motor de plantillas nativo de Flask. Permite insertar datos de Python en el HTML con `{{ variable }}` y lógica con `{% if %}`.

### Bootstrap 5
- **¿Por qué Bootstrap?** CSS pre-construido responsive. Permite hacer la UI rápido sin diseñar cada componente desde cero. Se usa la versión local (no CDN) para evitar dependencia de internet.

### Tailwind CSS
**¿Qué es?** Un framework CSS de "utilidades". En lugar de clases predefinidas como Bootstrap (`btn btn-primary`), Tailwind te da clases muy pequeñas y específicas (`text-blue-500 p-4 rounded-lg`) que combinas directamente en el HTML para construir el diseño.

**¿Cuál es la diferencia con Bootstrap?**
- Bootstrap: da componentes completos listos (botones, navbars, cards). Rápido pero todos los sitios se parecen.
- Tailwind: da piezas atómicas de CSS. Más control y diseño único, pero requiere más código en el HTML.

**¿Lo usamos en HogarFix?** En el backend principal (las plantillas Flask en `app/templates/`), **no**. Se usa Bootstrap 5. Tailwind sí está configurado en el formulario de registro de técnicos (`frontend/tech-registration/`) que es React + Vite. Hay un archivo `tailwind.config.js` y `postcss.config.js` en esa carpeta para procesarlo. Sin embargo, en las plantillas principales de Flask no se carga Tailwind CDN (el README original lo aclara).

### JavaScript (vanilla + Socket.IO)
- **¿Por qué vanilla JS y no React/Vue?** Para el frontend principal, HTML+JS es suficiente y más liviano. La única excepción es el formulario de registro de técnicos (`frontend/tech-registration/`) que usa React con Vite.
- **¿Por qué Socket.IO?** Para el chat de Fixi en tiempo real (WebSocket). Permite comunicación bidireccional sin polling HTTP.

### React + Vite (solo en el onboarding de técnicos)
- Solo para el formulario multipaso de registro de técnicos (`frontend/tech-registration/`). Tiene componentes como `SignaturePad`, `FileUploader`, validación con esquemas, etc.
- **¿Por qué React aquí?** El formulario tiene muchos pasos, validaciones complejas, firma digital y subida de múltiples archivos. React maneja mejor ese estado que HTML plano.

### PyMySQL
- Driver Python para conectar con MySQL. SQLAlchemy lo usa internamente.

### fpdf2
- Generación de PDFs en Python puro. Se usa para el contrato de técnicos.

### Authlib
- Maneja el flujo OAuth 2.0 / OpenID Connect con Google y Microsoft. Evita implementar manualmente el protocolo de autenticación.

### itsdangerous
- Genera tokens firmados con caducidad (se usa para los enlaces de recuperación de contraseña). Si alguien modifica el token, la firma falla.

### Groq
- Cliente Python para la API de Groq (IA). El chat de Fixi lo usa para generar respuestas inteligentes.

---

## 31. Arquitectura completa del proyecto — diagrama

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR (Cliente)                   │
│  HTML + CSS + JS + Bootstrap + Socket.IO.js             │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / WebSocket
┌────────────────────────▼────────────────────────────────┐
│                 SERVIDOR FLASK (Python)                  │
│  app/__init__.py  →  create_app()  →  App Factory        │
│                                                          │
│  Blueprints (módulos de rutas):                          │
│    auth.py       → /auth/...   (login, registro, OTP)   │
│    main.py       → /          (home, dashboard, búsqueda)│
│    booking.py    → /reservas/  (crear, completar)        │
│    technician.py → /tecnico/   (perfil, dashboard)       │
│    admin.py      → /admin/     (panel de administración) │
│    chat.py       → WebSocket   (Fixi IA en tiempo real)  │
│    api.py        → /api/       (endpoints JSON)          │
│                                                          │
│  Servicios:                                              │
│    otp.py              → genera/verifica OTP             │
│    email.py            → envía correos SMTP              │
│    contract_pdf.py     → genera PDF contrato             │
│    identity_verification.py → verifica docs técnicos     │
│                                                          │
│  Extensions:                                             │
│    SQLAlchemy (ORM)  Flask-Login  Flask-WTF (CSRF)       │
│    Flask-Limiter     Flask-SocketIO  Authlib (OAuth)     │
└────────┬───────────────────────┬────────────────────────┘
         │ SQL (PyMySQL)         │ HTTPS (API calls)
┌────────▼──────────┐  ┌────────▼────────────────────────┐
│  MySQL (XAMPP)    │  │  APIs Externas                   │
│  hogarfix_db      │  │  • Gmail SMTP (correo)           │
│  localhost:3306   │  │  • Groq API (IA chat Fixi)       │
│  Tablas: 10       │  │  • Google OAuth (login social)   │
└───────────────────┘  │  • Google Maps (geolocalización) │
                       └──────────────────────────────────┘

Archivos estáticos (fotos, docs):
  app/static/uploads/profile/       → fotos de perfil (cliente y técnico)
  app/static/uploads/verification/  → docs identidad técnicos (cédula, selfie)
  app/static/uploads/work/          → fotos portafolio del técnico
  app/static/uploads/evidence/      → fotos antes/después al completar reserva
  app/static/img/                   → logos y marca
```

---

## 32. No se usa Machine Learning propio

HogarFix **no implementa ni entrena modelos de Machine Learning**. No hay scikit-learn, TensorFlow, PyTorch ni ningún framework similar.

Lo que sí se usa:
- **Groq API**: consumo de un modelo de lenguaje externo ya entrenado para el chat Fixi.
- **Algoritmo de búsqueda de técnicos**: filtrado por localidad, especialidad y precio. Es lógica de consultas SQL, no ML.
- **Verificación de identidad**: actualmente en modo "mock" (simulado). Para producción se integraría con servicios como Onfido, que sí usan ML internamente, pero el código de HogarFix solo llama su API.

---

## 33. Flujo completo de un usuario nuevo — de A a Z

### Como cliente
```
1. Entra a http://localhost:5000
2. Hace clic en "Crear cuenta" → selecciona "Cliente"
3. Rellena el formulario (nombre, email, contraseña fuerte, teléfono, localidad)
4. Flask valida los datos (contraseña segura, email único, etc.)
5. Flask crea el usuario en la tabla "usuarios" con contraseña hasheada
6. Flask genera OTP y lo envía por correo
7. Usuario ingresa el OTP en la pantalla de verificación
8. Flask verifica HMAC, borra el OTP, inicia sesión
9. Correo de bienvenida enviado con logo Fixi
10. Redirige al dashboard del cliente
11. Puede buscar técnicos, reservar servicios, ver historial, dejar reseñas
```

### Como técnico
```
1. Entra a http://localhost:5000
2. Hace clic en "Crear cuenta" → selecciona "Técnico"
3. Completa el formulario multipaso de React (frontend/tech-registration/)
   → Información personal, documentos de identidad, especialidades, firma digital
4. Flask crea usuario + perfil técnico con estado "pending"
5. OTP por correo → verificación
6. El admin revisa los documentos y aprueba/rechaza
7. Una vez aprobado → técnico puede ver su dashboard, gestionar disponibilidad
8. Clientes pueden encontrarlo en la búsqueda y reservar servicios
9. Técnico ve reservas pendientes, las confirma, las completa con foto de evidencia
10. Puede descargar el contrato PDF firmado desde su perfil
```

---

## 34. Proceso de ejecución paso a paso (resumen operativo)

```
PASO 1: Iniciar MySQL
  → Abrir XAMPP Control Panel → Start MySQL
  → O desde terminal: C:\xampp\mysql\bin\mysqld.exe --defaults-file="C:\xampp\mysql\bin\my.ini"

PASO 2: Crear la base de datos (solo la primera vez)
  → Abrir phpMyAdmin en http://localhost/phpmyadmin
  → Ir a pestaña SQL → pegar contenido de schema.sql → Ejecutar
  → Si hay parches: ejecutar también schema_patch_payment.sql y schema_patch_evidence.sql

PASO 3: Preparar el entorno Python (solo la primera vez)
  cd C:\xampp\htdocs\Hogarfix
  py -m venv .venv
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\.venv\Scripts\Activate.ps1
  py -m pip install --upgrade pip
  py -m pip install -r requirements.txt

PASO 4: Configurar variables de entorno
  → Crear archivo .env en la raíz (copiar .env.example si existe)
  → Configurar: FLASK_SECRET_KEY, MAIL_USERNAME, MAIL_PASSWORD, GROQ_API_KEY, etc.

PASO 5: Iniciar el servidor Flask
  .\.venv\Scripts\Activate.ps1   ← activar entorno (cada vez que abres terminal)
  py app.py

PASO 6: Abrir en el navegador
  → http://localhost:5000
```

---

## 35. Variables de entorno (.env) — qué hace cada una

```env
# Seguridad
FLASK_SECRET_KEY=clave-secreta-larga-y-aleatoria   # Firma las cookies de sesión

# Base de datos
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=                                     # Vacío en XAMPP local
MYSQL_DB=hogarfix_db

# Correo SMTP
MAIL_ENABLED=true
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tmtomas62@gmail.com
MAIL_PASSWORD=contraseña-de-aplicacion-gmail
MAIL_FROM=tmtomas62@gmail.com
MAIL_TIMEOUT=20                                     # Segundos antes de timeout

# IA (chat Fixi)
GROQ_API_KEY=tu-api-key-de-groq                    # Sin esto Fixi usa solo FAQ local

# Google OAuth (login con Google)
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:5000/auth/google/callback

# Microsoft OAuth (login con Microsoft)
MICROSOFT_OAUTH_CLIENT_ID=...
MICROSOFT_OAUTH_CLIENT_SECRET=...

# Google Maps (geolocalización)
GOOGLE_MAPS_API_KEY=...

# Panel de administración
ADMIN_LOGIN_CODE=codigo-secreto-admin
ADMIN_REGISTER_CODE=codigo-secreto-registro-admin

# OTP
OTP_TTL_MINUTES=3
OTP_MAX_ATTEMPTS=3
```

---

## 36. Preguntas frecuentes para presentar el proyecto

**¿Es una app móvil?**
No. Es una aplicación web que se abre en el navegador. Es responsive (se adapta a móviles), pero no es una app nativa ni una APK.

**¿Está en producción / en internet?**
Actualmente corre en local (tu computador). El dominio `hogarfix.co` está pensado para la versión de producción. Para publicarla en internet se necesitaría un servidor en la nube (VPS con Nginx + Gunicorn + SSL).

**¿Por qué no se usa WordPress o Shopify?**
Porque HogarFix tiene lógica de negocio específica: verificación de identidad de técnicos, OTP, disponibilidad, contratos PDF, chat en tiempo real con IA. Eso no lo da ningún CMS genérico sin personalización masiva.

**¿Es escalable?**
La arquitectura con Flask Blueprints y SQLAlchemy permite escalar. Para producción real se recomendaría: PostgreSQL en lugar de MySQL, Gunicorn + Nginx en Linux, Redis para sesiones y rate limiting, almacenamiento en la nube (S3/Cloudinary) para archivos.

**¿Quién hizo el proyecto?**
Desarrollado íntegramente con Python/Flask. El representante legal del contrato es **Tomas Garcia Guevara, C.C. 1029144798**.

**¿Tiene inteligencia artificial?**
Sí, en el chat de Fixi mediante la API de **Groq**. No entrena modelos propios. La IA responde preguntas sobre la plataforma en tiempo real.

---

# GLOSARIO DE CONCEPTOS CLAVE — HOGARFIX
> Definición corta de cada término técnico usado en el proyecto. Ideal para explicarle el proyecto a alguien sin experiencia en programación o para repasar antes de una presentación.

---

## 37. Conceptos generales de programación web

### API (Application Programming Interface)
**¿Qué es?** Un canal de comunicación entre dos sistemas. Un sistema pregunta, el otro responde con datos.
**¿Cómo lo usamos?** El servidor Flask se comunica con APIs externas: le pregunta a Groq por una respuesta de IA, le pregunta a Google por los datos del usuario que inicia sesión, le pregunta a Gmail que envíe un correo.

### API Key (Clave de API)
**¿Qué es?** Una contraseña especial que identifica quién está haciendo la petición a un servicio externo. Sin ella, el servicio rechaza la solicitud.
**¿Cómo lo usamos?** Tenemos tres API Keys en el proyecto:
- `GROQ_API_KEY` → le da acceso al servidor para hablar con la IA de Groq (chat Fixi).
- `GOOGLE_MAPS_API_KEY` → permite mostrar y buscar ubicaciones en el mapa.
- `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` → son las credenciales que Google le da a HogarFix para poder usar "Iniciar sesión con Google".

Todas se guardan en el archivo `.env`, nunca en el código fuente.

### Servidor
**¿Qué es?** Un programa que está siempre encendido esperando peticiones. Cuando alguien entra a la web, el servidor recibe la petición y responde con la página.
**¿Cómo lo usamos?** Flask es el servidor. Se ejecuta con `py app.py` y queda escuchando en `http://localhost:5000`.

### Cliente
**¿Qué es?** El que hace las peticiones al servidor. En web, el cliente es el navegador (Chrome, Firefox, etc.).
**¿Cómo lo usamos?** El navegador del usuario es el cliente. Cuando escribe `localhost:5000` y presiona Enter, el navegador le pide la página al servidor Flask.

### HTTP / HTTPS
**¿Qué es?** El protocolo (idioma) que usan el navegador y el servidor para comunicarse. HTTP es sin cifrado, HTTPS es con cifrado (más seguro).
**¿Cómo lo usamos?** En desarrollo usamos HTTP (`http://localhost:5000`). En producción se usaría HTTPS para cifrar todos los datos en tránsito.

### WebSocket
**¿Qué es?** Una conexión permanente entre navegador y servidor que permite enviar mensajes en tiempo real en ambas direcciones, sin que el usuario tenga que recargar la página.
**¿Cómo lo usamos?** El chat de Fixi usa WebSocket. Cuando el usuario escribe un mensaje, llega al servidor al instante, y la respuesta de la IA vuelve al navegador sin recargar. Lo maneja la librería `Flask-SocketIO`.

### Frontend
**¿Qué es?** Todo lo que el usuario ve en el navegador: HTML (estructura), CSS (diseño) y JavaScript (interactividad).
**¿Cómo lo usamos?** Las plantillas Jinja2 en `app/templates/`, los estilos en `app/static/css/app.css` y los scripts en `app/static/js/`. También el formulario de registro de técnicos en `frontend/tech-registration/` (React).

### Backend
**¿Qué es?** El servidor, la lógica de negocio y la base de datos. El usuario no lo ve directamente.
**¿Cómo lo usamos?** Flask + los blueprints + los modelos + los servicios. Todo en la carpeta `app/`.

---

## 38. Archivos clave del proyecto — qué es y para qué sirve cada uno

### `.env`
**¿Qué es?** Archivo de texto que guarda variables de entorno: contraseñas, claves de API, configuración de correo, etc. No se sube a GitHub (está en `.gitignore`).
**¿Cómo lo usamos?** Flask lee este archivo al arrancar gracias a la librería `python-dotenv`. Todo lo sensible (claves, contraseñas) va aquí, no en el código. Así si alguien ve el código, no ve las contraseñas.
**Ejemplo de variables:**
```
FLASK_SECRET_KEY, MYSQL_PASSWORD, MAIL_PASSWORD, GROQ_API_KEY, GOOGLE_OAUTH_CLIENT_ID
```

### `config.py`
**¿Qué es?** Archivo Python que lee el `.env` y convierte las variables en configuración de Flask.
**¿Cómo lo usamos?** Define la URL de conexión a MySQL, la configuración de correo, límites de tamaño de archivo, claves de APIs. Flask lo carga con `app.config.from_object(Config)` al arrancar.

### `app.py`
**¿Qué es?** El punto de entrada del proyecto. El archivo que se ejecuta con `py app.py`.
**¿Cómo lo usamos?** Llama a `create_app()` para construir la aplicación Flask y arranca el servidor con `socketio.run()` en el puerto 5000.

### `app/__init__.py`
**¿Qué es?** El corazón de la aplicación. La función `create_app()` vive aquí.
**¿Cómo lo usamos?** Crea la app Flask, carga la configuración, inicializa todas las extensiones (DB, login, CSRF, etc.), registra todos los blueprints y define los manejadores de errores (404, 500, etc.).

### `app/models.py`
**¿Qué es?** Define las tablas de la base de datos como clases Python (ORM). Cada clase es una tabla.
**¿Cómo lo usamos?** Por ejemplo, `class User` representa la tabla `usuarios`. Cuando Flask crea un usuario, crea un objeto `User` y SQLAlchemy lo convierte en un `INSERT` de SQL. Tablas definidas aquí: `User`, `TechnicianProfile`, `Booking`, `Review`, `Availability`, `OTPVerification`, `UserSession`, `LoginLog`, `Notification`.

### `app/extensions.py`
**¿Qué es?** Instancia las extensiones de Flask una sola vez para evitar importaciones circulares.
**¿Cómo lo usamos?** Aquí se crean los objetos `db`, `login_manager`, `socketio`, `oauth`, `csrf`, `limiter`. Luego `__init__.py` los inicializa con la app real.

### `app/utils.py`
**¿Qué es?** Funciones de utilidad que usan varios módulos del proyecto.
**¿Cómo lo usamos?** Contiene: envío de correos SMTP, subida segura de archivos, decorador `role_required` (control de acceso por rol), envío de alertas y OTP por correo.

### `schema.sql`
**¿Qué es?** Script SQL que crea todas las tablas de la base de datos desde cero.
**¿Cómo lo usamos?** Se importa en phpMyAdmin la primera vez que se configura el proyecto. Define la estructura exacta de cada tabla: columnas, tipos de datos, claves primarias, claves foráneas, índices.
**Tablas que crea:** `usuarios`, `tecnicos`, `reservas`, `disponibilidad`, `resenas`, `otp_verifications`, `user_sessions`, `logs_login`, `notificaciones`, `policy_acceptances`.

### `schema_patch_payment.sql`
**¿Qué es?** Un parche SQL que agrega la columna `payment_method` a la tabla `reservas`.
**¿Cómo lo usamos?** Se ejecuta después del `schema.sql` si la base ya existía. Permite registrar si el pago fue en efectivo, transferencia, Nequi o Daviplata.

### `schema_patch_evidence.sql`
**¿Qué es?** Parche SQL que agrega columnas de evidencia fotográfica y notas al completar una reserva.
**¿Cómo lo usamos?** Se ejecuta en bases existentes para añadir `evidence_photos` y `completion_note` a la tabla `reservas`.

### `requirements.txt`
**¿Qué es?** Lista de todas las librerías Python que necesita el proyecto, con versiones exactas.
**¿Cómo lo usamos?** Con `py -m pip install -r requirements.txt` se instalan todas de una sola vez. Garantiza que todos usen las mismas versiones.

---

## 39. Librerías y servicios externos — definición y uso en HogarFix

### Flask
**¿Qué es?** Framework web ligero para Python. Permite crear un servidor web con rutas, templates y extensiones.
**En el proyecto:** Es el motor de todo el backend. Maneja cada URL que el usuario visita.

### Flask-SQLAlchemy / SQLAlchemy
**¿Qué es?** Son dos cosas unidas:
- **SQLAlchemy**: la librería base que sabe hablar con bases de datos SQL. Funciona como un traductor: tú escribes Python, ella genera el SQL correcto para MySQL (o cualquier otro motor).
- **Flask-SQLAlchemy**: el puente que integra SQLAlchemy dentro de Flask para que funcionen juntos sin configuración manual.

**¿Qué es un ORM?** ORM = Object-Relational Mapper. Significa que cada tabla de la base de datos se representa como una clase Python, y cada fila de esa tabla es un objeto. En lugar de escribir `SELECT * FROM usuarios WHERE email = 'x'`, escribes `User.query.filter_by(email='x').first()` en Python y SQLAlchemy genera el SQL por ti.

**¿Por qué usarlo en lugar de SQL directo?**
- Más seguro: previene SQL Injection automáticamente.
- Más legible: el código es Python, no mezcla de strings SQL.
- Más mantenible: si cambias de MySQL a PostgreSQL, casi no cambia el código.

**En el proyecto:** Todas las operaciones de base de datos se hacen con Python:
- `db.session.add(nuevo_usuario)` → `INSERT INTO usuarios ...`
- `User.query.filter_by(email=email).first()` → `SELECT * FROM usuarios WHERE email = ...`
- `db.session.commit()` → confirma los cambios en la base de datos
- `db.session.delete(reserva)` → `DELETE FROM reservas WHERE id = ...`

### Flask-Login
**¿Qué es?** Maneja las sesiones de usuario (quién está logueado, proteger rutas).
**En el proyecto:** El decorador `@login_required` bloquea rutas si el usuario no está autenticado. `current_user` da acceso al usuario logueado en cualquier plantilla o ruta.

### Flask-WTF / WTForms
**¿Qué es?** Protección CSRF para formularios. Genera y valida un token oculto en cada formulario para que no pueda ser enviado desde otra página.
**En el proyecto:** Todos los formularios HTML incluyen `{{ form.hidden_tag() }}` o el token CSRF. Evita que alguien externo haga acciones en nombre del usuario.

### Flask-Limiter
**¿Qué es?** Limita cuántas veces se puede llamar a una ruta en un período de tiempo (rate limiting).
**En el proyecto:** Protege el login, el registro y el envío de OTP contra ataques de fuerza bruta. Por ejemplo, máximo 5 intentos de login por minuto desde la misma IP.

### Flask-SocketIO
**¿Qué es?** Agrega soporte WebSocket a Flask. Permite comunicación en tiempo real bidireccional.
**En el proyecto:** Maneja el chat de Fixi. El navegador envía un mensaje, Flask lo recibe por WebSocket, consulta a Groq, y devuelve la respuesta en tiempo real.

### PyMySQL
**¿Qué es?** Driver (conector) Python puro para conectar con bases de datos MySQL.
**En el proyecto:** SQLAlchemy lo usa internamente para hablar con MySQL de XAMPP. Se configura en la URL `mysql+pymysql://...`.

### Authlib
**¿Qué es?** Librería que implementa los protocolos OAuth 2.0 y OpenID Connect para autenticación social.
**En el proyecto:** Maneja el flujo completo de "Iniciar sesión con Google" y "Iniciar sesión con Microsoft". Sin ella habría que implementar el protocolo OAuth manualmente.

### python-dotenv
**¿Qué es?** Carga las variables del archivo `.env` como variables de entorno de Python.
**En el proyecto:** `config.py` llama a `load_dotenv()` al arrancar y así Flask puede leer `MYSQL_PASSWORD`, `GROQ_API_KEY`, etc. desde el `.env`.

### itsdangerous
**¿Qué es?** Genera tokens firmados digitalmente con caducidad. Si alguien modifica el token, la firma falla.
**En el proyecto:** Se usa para los enlaces de recuperación de contraseña. El link contiene un token firmado con el SECRET_KEY. Si expira o se manipula, Flask lo rechaza.

### fpdf2
**¿Qué es?** Librería para generar archivos PDF en Python puro, sin necesitar programas externos.
**En el proyecto:** Genera el contrato de prestación de servicios del técnico en PDF con logo, firmas y datos del contrato.

### Groq (librería + API)
**¿Qué es?** La librería oficial de Groq para Python. Groq es un servicio de IA en la nube que ofrece modelos de lenguaje (LLM) con velocidad extremadamente alta.
**En el proyecto:** El chat de Fixi le envía el mensaje del usuario a Groq y recibe una respuesta generada por IA. Se necesita `GROQ_API_KEY` en el `.env`.
**¿Dónde se usa?** `app/blueprints/chat.py` → función `_get_groq_client()`.

### Werkzeug
**¿Qué es?** Librería WSGI de bajo nivel que usa Flask internamente. También provee utilidades como `generate_password_hash`, `check_password_hash` y `secure_filename`.
**En el proyecto:** Se usa para hashear contraseñas (`set_password` / `check_password` en `models.py`) y para sanear nombres de archivo al subir imágenes (`secure_filename` en `utils.py`).

### eventlet
**¿Qué es?** Servidor WSGI asíncrono que permite manejar muchas conexiones simultáneas, necesario para WebSocket.
**En el proyecto:** Flask-SocketIO lo usa internamente para soportar WebSocket cuando se ejecuta `py app.py`. Sin eventlet, WebSocket no funcionaría.

### requests
**¿Qué es?** Librería Python para hacer peticiones HTTP a otras APIs.
**En el proyecto:** Se usa en `services/identity_verification.py` para llamar a APIs externas de verificación de identidad (como Onfido en producción).

---

## 40. Credenciales y API Keys — de dónde vienen y para qué sirven

| Variable en `.env` | Servicio | Para qué sirve | Dónde se obtiene |
|---|---|---|---|
| `GROQ_API_KEY` | Groq | Permite al chat Fixi usar IA para responder | console.groq.com → API Keys |
| `GOOGLE_OAUTH_CLIENT_ID` | Google Cloud | Identificador de HogarFix ante Google para login social | console.cloud.google.com → Credentials |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google Cloud | Contraseña secreta de la app ante Google | console.cloud.google.com → Credentials |
| `GOOGLE_MAPS_API_KEY` | Google Maps | Muestra mapas y busca ubicaciones de localidades | console.cloud.google.com → Maps API |
| `MICROSOFT_OAUTH_CLIENT_ID` | Azure AD | Identificador de HogarFix ante Microsoft para login social | portal.azure.com → App Registrations |
| `MICROSOFT_OAUTH_CLIENT_SECRET` | Azure AD | Contraseña secreta de la app ante Microsoft | portal.azure.com → Certificates & secrets |
| `MAIL_PASSWORD` | Gmail | Contraseña de aplicación (no la real) para enviar correos SMTP | Cuenta Gmail → Seguridad → Contraseñas de app |
| `FLASK_SECRET_KEY` | Flask (interno) | Firma y cifra las cookies de sesión | Generar aleatoriamente: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_LOGIN_CODE` | HogarFix (interno) | Código para acceder al panel de administración | Lo defines tú en el `.env` |
| `ADMIN_REGISTER_CODE` | HogarFix (interno) | Código para registrar una cuenta de admin | Lo defines tú en el `.env` |

### ¿Por qué no se hardcodean estas claves en el código?
Si alguien ve el código (en GitHub, por ejemplo), vería todas las contraseñas. Con `.env` + `.gitignore`, el archivo `.env` nunca se sube al repositorio. Cada desarrollador tiene su propio `.env` local.

### ¿Cuál es la diferencia entre Client ID y Client Secret en OAuth?
- **Client ID**: es público, identifica la app. Como el nombre de usuario.
- **Client Secret**: es privado, autentica la app. Como la contraseña. Nunca debe ser público.

---

## 41. Conceptos de base de datos usados en HogarFix

### ORM (Object-Relational Mapper)
**¿Qué es?** Traduce objetos Python a registros de base de datos y viceversa. Escribe Python, él genera el SQL.
**En el proyecto:** SQLAlchemy. `User.query.all()` equivale a `SELECT * FROM usuarios`.

### Migración / Schema
**¿Qué es?** El "plano" de la base de datos. Define qué tablas existen, qué columnas tienen y cómo se relacionan.
**En el proyecto:** `schema.sql` es el schema completo. Los archivos `schema_patch_*.sql` son migraciones (cambios incrementales al schema original).

### Clave primaria (PRIMARY KEY)
**¿Qué es?** El identificador único de cada fila de una tabla. No puede repetirse.
**En el proyecto:** La columna `id` en todas las tablas (`usuarios.id`, `reservas.id`, etc.).

### Clave foránea (FOREIGN KEY)
**¿Qué es?** Una columna que apunta al `id` de otra tabla, creando una relación entre ellas.
**En el proyecto:** `reservas.client_id` apunta a `usuarios.id` (quién reservó). `reservas.technician_id` también apunta a `usuarios.id` (a quién reservó).

### Relación 1:1 (uno a uno)
**¿Qué es?** Un registro de la tabla A tiene exactamente un registro en la tabla B.
**En el proyecto:** Un usuario técnico tiene exactamente un perfil técnico (`usuarios` ↔ `tecnicos`).

### Relación 1:N (uno a muchos)
**¿Qué es?** Un registro de la tabla A puede tener muchos registros en la tabla B.
**En el proyecto:** Un cliente puede tener muchas reservas. Un técnico puede tener muchas reservas.

### Hash (de contraseña)
**¿Qué es?** Transformación irreversible de un texto. Convierte "miContraseña123!" en una cadena incomprensible. No se puede revertir.
**En el proyecto:** Las contraseñas se guardan hasheadas con bcrypt (via Werkzeug). Si alguien roba la base de datos, no puede leer las contraseñas.

### HMAC (Hash-based Message Authentication Code)
**¿Qué es?** Un hash que además usa una clave secreta. Solo quien tiene la clave puede verificar que el hash es correcto.
**En el proyecto:** El código OTP se hashea con HMAC-SHA256 usando el `SECRET_KEY` de Flask. Así el OTP en la DB no puede ser leído ni falsificado.

### Índice (INDEX)
**¿Qué es?** Una estructura que acelera las búsquedas en una columna específica.
**En el proyecto:** Las columnas `email`, `oauth_provider` y `oauth_subject` tienen índice porque se buscan con frecuencia (en cada login).

### MariaDB
**¿Qué es?** Una base de datos de código abierto que nació como una bifurcación ("fork") de MySQL. Es prácticamente idéntica a MySQL en comandos, sintaxis SQL y comportamiento, pero con algunas mejoras de rendimiento y licencia más abierta.

**¿Por qué aparece en nuestro proyecto si decimos que usamos MySQL?** Porque XAMPP instala MariaDB en lugar de MySQL original. Son tan compatibles que:
- phpMyAdmin los trata igual.
- SQLAlchemy se conecta igual con `mysql+pymysql://...`.
- El `schema.sql` funciona igual en los dos.
- El código de Flask no nota ninguna diferencia.

**En resumen:** cuando decimos "MySQL" en este proyecto, técnicamente estamos usando MariaDB 10.x de XAMPP. No hay que cambiar nada, funcionan exactamente igual para nuestro caso de uso.

### InnoDB
**¿Qué es?** El motor de almacenamiento de MySQL/MariaDB. Es el "cómo" se guardan y gestionan los datos en disco dentro del motor de base de datos.
**¿Por qué importa?** InnoDB soporta claves foráneas (`FOREIGN KEY`) y transacciones (operaciones que se confirman o revierten completas). El motor alternativo (MyISAM) no soporta claves foráneas.
**En el proyecto:** Todas las tablas usan `ENGINE=InnoDB`. Esto garantiza que las relaciones entre tablas (`reservas.client_id` → `usuarios.id`, etc.) sean respetadas por la base de datos.

### utf8mb4
**¿Qué es?** Codificación de caracteres que soporta todo el Unicode, incluyendo emojis y acentos.
**En el proyecto:** La base `hogarfix_db` usa `CHARACTER SET utf8mb4` para soportar correctamente tildes (á, é, í, ó, ú, ñ) y caracteres especiales del español colombiano.

---

## 42. Conceptos de seguridad usados en HogarFix

### CSRF (Cross-Site Request Forgery)
**¿Qué es?** Ataque donde una web maliciosa hace que el navegador del usuario ejecute acciones en otra web donde está logueado.
**Cómo lo prevenimos:** Flask-WTF genera un token único en cada formulario. Si el formulario no viene del sitio correcto, el token no coincide y Flask rechaza la petición.

### Rate Limiting (límite de velocidad)
**¿Qué es?** Restricción de cuántas veces se puede llamar a una ruta en un tiempo determinado.
**Cómo lo usamos:** Flask-Limiter bloquea IPs que intenten hacer login, registro o envío de OTP demasiadas veces seguidas. Previene ataques de fuerza bruta.

### OTP (One-Time Password)
**¿Qué es?** Contraseña de un solo uso y tiempo limitado (6 dígitos, expira en 3 minutos).
**Cómo lo usamos:** Se envía al correo al hacer login. El servidor lo verifica con HMAC. Es el segundo factor de autenticación (2FA).

### 2FA (Two-Factor Authentication)
**¿Qué es?** Doble verificación de identidad: algo que sabes (contraseña) + algo que tienes (acceso al correo).
**Cómo lo usamos:** Después del email+contraseña correctos, se pide el OTP del correo. Ambos deben ser correctos para entrar.

### Token de sesión
**¿Qué es?** Un identificador cifrado guardado en una cookie del navegador que dice "este navegador es el usuario X".
**Cómo lo usamos:** Flask-Login lo gestiona automáticamente. El `SECRET_KEY` del `.env` firma la cookie. Si alguien intenta falsificarla, la firma no coincide.

### Secure Filename
**¿Qué es?** Función que limpia el nombre de un archivo subido, eliminando caracteres peligrosos (`../`, etc.).
**Cómo lo usamos:** `secure_filename()` de Werkzeug en `utils.py` al guardar fotos de perfil o documentos. Evita que alguien suba un archivo con nombre `../../app/__init__.py` para sobrescribir código.

### OAuth 2.0
**¿Qué es?** Protocolo estándar que permite a una app (HogarFix) usar la identidad del usuario de otro servicio (Google) sin conocer su contraseña.
**Cómo lo usamos:** Login con Google y Microsoft. HogarFix nunca ve la contraseña de Google del usuario.

### OpenID Connect
**¿Qué es?** Capa sobre OAuth 2.0 que añade información de identidad (nombre, email, foto). Es la extensión que permite el login social.
**Cómo lo usamos:** Junto con OAuth, cuando el usuario autoriza con Google, recibimos un `id_token` con email y nombre.

### itsdangerous / Tokens firmados
**¿Qué es?** Tokens de texto con firma criptográfica y caducidad. Si expiran o se modifican, son inválidos.
**Cómo lo usamos:** Los enlaces de recuperación de contraseña contienen un token firmado. Si el usuario intenta usarlo después de 1 hora o modifica la URL, Flask lo rechaza.

---

## 43. Conceptos de arquitectura

### Blueprint (Flask)
**¿Qué es?** Un módulo de rutas agrupadas por dominio funcional. Permite dividir la aplicación en partes independientes.
**En el proyecto:** Hay 7 blueprints: `auth`, `main`, `booking`, `technician`, `admin`, `chat`, `api`. Cada uno maneja un área del negocio.

### App Factory (`create_app`)
**¿Qué es?** Patrón de diseño donde la app Flask no se crea al importar el módulo, sino al llamar una función `create_app()`. Permite configurar la app con diferentes configuraciones (producción, pruebas, desarrollo).
**En el proyecto:** `app/__init__.py` define `create_app()`. `app.py` la llama para obtener la app configurada.

### Jinja2
**¿Qué es?** Motor de plantillas de Python. Permite escribir HTML con variables, bucles y condicionales de Python.
**En el proyecto:** Todas las páginas son plantillas `.html` en `app/templates/`. Flask pasa datos Python al template con `render_template("pagina.html", usuario=user)` y Jinja2 los inserta en el HTML.

### WSGI (Web Server Gateway Interface)
**¿Qué es?** El estándar que define cómo un servidor web se comunica con una aplicación Python.
**En el proyecto:** Flask es una aplicación WSGI. En desarrollo la ejecuta Werkzeug (incluido en Flask). En producción la ejecutaría Gunicorn o uWSGI.

### Entorno virtual (`.venv`)
**¿Qué es?** Carpeta aislada con Python y las librerías del proyecto. Evita conflictos con otras versiones instaladas globalmente.
**En el proyecto:** Se crea con `py -m venv .venv` y se activa con `.\.venv\Scripts\Activate.ps1`. Todas las librerías de `requirements.txt` se instalan dentro de esta carpeta.

### Modelo MVC (Model-View-Controller) adaptado
**¿Qué es?** Patrón de arquitectura que separa datos (Model), presentación (View) y lógica (Controller).
**En el proyecto (adaptado a Flask):**
- **Model** → `app/models.py` (tablas y relaciones)
- **View** → `app/templates/*.html` (lo que ve el usuario)
- **Controller** → `app/blueprints/*.py` (lógica de rutas y negocio)

---

## 44. Términos complementarios — librerías visuales, formatos y protocolos

### CDN (Content Delivery Network)
**¿Qué es?** Red de servidores distribuidos por el mundo que sirven archivos estáticos (CSS, JS, imágenes) desde el servidor más cercano al usuario, haciendo que carguen más rápido.
**En el proyecto:** AOS, GSAP y Bootstrap Icons se cargan desde CDN externo (`unpkg.com`, `cdn.jsdelivr.net`). Bootstrap 5 y Socket.IO se sirven en local desde `app/static/` para no depender de internet en desarrollo.
**Ventaja del CDN:** el archivo ya está en caché en el navegador del usuario si otra web lo usó antes. Carga más rápido.
**Riesgo del CDN:** si el CDN cae, el recurso no carga. Por eso Bootstrap se tiene en local.

### AOS (Animate On Scroll)
**¿Qué es?** Librería JavaScript pequeña que anima elementos de la página cuando el usuario hace scroll y los elementos entran en la pantalla (fade-in, slide-up, zoom, etc.).
**En el proyecto:** Se carga desde CDN en `app/templates/base.html`. Se inicializa con:
```javascript
AOS.init({ duration: 650, once: true, offset: 80, easing: 'ease-out-cubic' });
```
Se aplica con el atributo `data-aos="fade-up"` en los elementos HTML que se quieren animar. El footer, cards de servicios y otras secciones lo usan para dar sensación de fluidez al navegar.

### GSAP + ScrollTrigger
**¿Qué es?** GSAP (GreenSock Animation Platform) es la librería de animaciones JavaScript más potente y precisa del mercado. ScrollTrigger es un plugin de GSAP que ejecuta animaciones cuando el usuario llega a cierta parte de la página al hacer scroll.
**En el proyecto:** Solo se usa en `app/templates/main/home.html` (la página de inicio). Anima el hero (título principal), las cards de servicios, los pasos "¿Cómo funciona?", la galería y los títulos de sección. Se carga desde CDN con fallback: si falla, la página funciona igual pero sin animaciones.
**Diferencia con AOS:** AOS es más simple (solo un atributo HTML). GSAP da control total sobre duración, dirección, stagger (animaciones escalonadas), easing personalizado, etc.

### Bootstrap Icons
**¿Qué es?** Biblioteca de más de 2.000 iconos SVG en formato de fuente de iconos (similar a Font Awesome). Se usa con clases CSS: `<i class="bi bi-house"></i>`.
**En el proyecto:** Se carga desde CDN. Se usa en toda la plataforma para iconos de menú, botones, estados de reservas, formularios, etc.

### JSON (JavaScript Object Notation)
**¿Qué es?** Formato de texto ligero para guardar y transportar datos estructurados. Se ve así: `{"nombre": "Juan", "edad": 25}`. Es legible por humanos y por máquinas.
**En el proyecto:** Se usa en varios lugares:
- `TechnicianProfile.bio` → guarda toda la información extendida del técnico como JSON en una columna `TEXT` de la DB: `{"service_description": "...", "base_price": 50000, "charge_type": "hora", "signature_data": "..."}`.
- `work_photos` y `evidence_photos` → listas de rutas de fotos guardadas como JSON: `["uploads/work/foto1.jpg", "uploads/work/foto2.jpg"]`.
- Las respuestas del blueprint `api.py` → se devuelven como JSON al navegador.
- El chat de Fixi → los mensajes se envían como JSON por WebSocket.

### SMTP (Simple Mail Transfer Protocol)
**¿Qué es?** El protocolo estándar de internet para enviar correos electrónicos. Es el "idioma" que usan los servidores de correo para transferir mensajes.
**En el proyecto:** Flask se conecta directamente al servidor SMTP de Gmail (`smtp.gmail.com`, puerto 587) para enviar correos de bienvenida, OTP, alertas y recuperación de contraseña. La librería usada es `smtplib` (incluida en Python, no requiere instalación).
**¿Por qué puerto 587?** Es el puerto estándar para SMTP con STARTTLS (cifrado). El puerto 465 es para SSL directo. El 25 está bloqueado por la mayoría de proveedores por abuso de spam.

### Base64
**¿Qué es?** Sistema de codificación que convierte datos binarios (imágenes, archivos) en texto ASCII. Una imagen se convierte en una cadena larga de letras y números que se puede incluir directamente en HTML o JSON.
**En el proyecto:** El componente `SignaturePad` del formulario React captura la firma digital del técnico y la convierte a Base64 (`data:image/png;base64,...`). Ese string se envía al servidor y se guarda en `bio["signature_data"]`. Luego `contract_pdf.py` lo decodifica para insertar la firma en el PDF del contrato.

### Bcrypt
**¿Qué es?** Algoritmo de hash diseñado específicamente para contraseñas. A diferencia de SHA-256, Bcrypt es lento a propósito (incluye un "factor de costo") para dificultar ataques de fuerza bruta, y genera un salt automáticamente para que dos contraseñas iguales den hashes distintos.
**En el proyecto:** Werkzeug lo usa internamente en `generate_password_hash()` y `check_password_hash()`. Cuando el usuario crea o cambia su contraseña, Bcrypt la transforma en algo como `$2b$12$...` que se guarda en `usuarios.password_hash`. Nunca se guarda la contraseña real.

### SHA-256 (Secure Hash Algorithm 256 bits)
**¿Qué es?** Función criptográfica que convierte cualquier texto en una huella digital de 256 bits (64 caracteres hexadecimales). Es irreversible: no se puede obtener el texto original a partir del hash.
**En el proyecto:** Se usa combinado con HMAC para hashear los códigos OTP. `HMAC-SHA256(clave_secreta, sal + código)` produce el hash que se guarda en `otp_verifications`. Al verificar, se rehace el mismo cálculo y se compara.

### Cookie / Cookie de sesión
**¿Qué es?** Pequeño archivo de texto que el servidor guarda en el navegador del usuario. En cada petición siguiente, el navegador lo envía de vuelta al servidor automáticamente.
**En el proyecto:** Flask-Login usa una cookie de sesión firmada con el `FLASK_SECRET_KEY`. Cuando el usuario hace login, el servidor guarda en la cookie un token que identifica su sesión. Cuando vuelve a entrar, el servidor lee la cookie y sabe quién es sin pedirle que se identifique de nuevo. La cookie está firmada criptográficamente: si alguien la modifica, la firma falla y Flask la rechaza.

### Responsive Design (Diseño Responsivo)
**¿Qué es?** Técnica de diseño web en la que la página se adapta automáticamente al tamaño de la pantalla del dispositivo (PC, tablet, móvil) sin necesidad de una app separada.
**En el proyecto:** Se logra con Bootstrap 5 (sistema de grillas de 12 columnas con breakpoints `sm`, `md`, `lg`, `xl`) y con media queries propias en `app/static/css/app.css`. El navbar colapsa en móvil, las cards se apilan en pantallas pequeñas, los paneles de técnico se reorganizan, etc.

### Vite
**¿Qué es?** Herramienta de construcción (build tool) para proyectos JavaScript modernos. Sirve el código en desarrollo con recarga instantánea (Hot Module Replacement) y empaqueta el código para producción de forma muy rápida.
**En el proyecto:** Se usa en `frontend/tech-registration/` para el formulario React de registro de técnicos. Se inicia con `npm run dev` (desarrollo) o `npm run build` (producción). El archivo `vite.config.js` lo configura.

### PostCSS
**¿Qué es?** Herramienta que procesa CSS con plugins. Tailwind CSS lo usa para escanear el HTML/JSX, encontrar qué clases de Tailwind se usan, y generar solo el CSS necesario (eliminando el resto para reducir el tamaño del archivo final).
**En el proyecto:** El archivo `frontend/tech-registration/postcss.config.js` lo configura para trabajar con Tailwind en el formulario React. No afecta el CSS del backend Flask.

### SignaturePad
**¿Qué es?** Componente React (`frontend/tech-registration/src/components/SignaturePad.jsx`) que muestra un lienzo (canvas) donde el técnico puede dibujar su firma con el mouse o el dedo en pantalla táctil.
**En el proyecto:** El técnico firma al final del formulario de registro. La firma se captura como imagen Base64, se envía al servidor y se guarda en el campo `bio["signature_data"]` del perfil técnico. `contract_pdf.py` la usa para insertar la firma real del técnico en el contrato PDF.

### Bootstrap Icons
**¿Qué es?** Ya definido arriba (sección CDN). Adicionalmente: cada icono tiene un nombre tipo `bi-house`, `bi-person`, `bi-calendar`, `bi-star`, etc. Se insertan en HTML con `<i class="bi bi-nombre-icono"></i>`.
**En el proyecto:** Usados en toda la UI: iconos del menú lateral del técnico, botones de acciones en reservas, indicadores de estado, formularios, etc.

### Pool de conexiones
**¿Qué es?** Conjunto de conexiones a la base de datos que se mantienen abiertas y se reutilizan. Abrir y cerrar una conexión a MySQL tiene un costo de tiempo; el pool las mantiene listas para usar.
**En el proyecto:** SQLAlchemy gestiona un pool automáticamente. Cuando Flask recibe muchas peticiones simultáneas, no abre una conexión nueva por cada una, sino que reutiliza las del pool. Esto hace la app más eficiente.

### Decorador Python (`@`)
**¿Qué es?** Una función que envuelve a otra función para añadirle comportamiento extra sin modificar su código. Se escribe con `@nombre_decorador` encima de la función.
**En el proyecto:** Se usan varios decoradores clave:
- `@login_required` → bloquea la ruta si el usuario no está logueado.
- `@role_required('tecnico')` → bloquea si el rol no coincide.
- `@auth_bp.route('/login')` → registra la función como manejador de la URL `/login`.
- `@limiter.limit("5 per minute")` → aplica rate limiting a esa ruta.

---

## 45. Términos que faltan — servicios en la nube, funciones Flask y React

### Cloudinary
**¿Qué es?** Servicio en la nube para subir, almacenar, transformar y servir imágenes y videos. Las fotos se guardan en sus servidores y se acceden por URL pública.
**En el proyecto:** El archivo `frontend/tech-registration/src/services/cloudinary.js` tiene preparada la integración. En el MVP actual las fotos se guardan en disco local (`app/static/uploads/`). Cloudinary está listo para activarse en producción definiendo `VITE_CLOUDINARY_CLOUD_NAME` y `VITE_CLOUDINARY_UPLOAD_PRESET` en el `.env` del frontend.
**¿Por qué usarlo en producción?** Los archivos locales se pierden si el servidor se reinicia o cambia. Cloudinary los mantiene en la nube, sirve imágenes optimizadas por tamaño y formato, y da URLs permanentes.

### Firebase / Firebase Auth
**¿Qué es?** Plataforma de Google para aplicaciones web y móviles. Firebase Auth es su servicio de autenticación: maneja login con email, Google, Facebook, teléfono (SMS), etc.
**En el proyecto:** El archivo `frontend/tech-registration/src/services/firebaseOtp.js` tiene preparada la verificación de teléfono por SMS usando Firebase Auth. Actualmente el backend Flask usa OTP por correo. Firebase Phone OTP está preparado para activarse cuando se quiera verificar el número de celular del técnico al registrarse.
**¿Qué necesita para activarse?** Crear un proyecto en Firebase Console, habilitar "Phone" en Authentication, y definir las variables `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_APP_ID` en el `.env` del frontend.

### reCAPTCHA
**¿Qué es?** Sistema de Google que distingue humanos de bots en formularios. La versión invisible (`RecaptchaVerifier` con `size: "invisible"`) actúa en segundo plano sin mostrar el clásico "No soy un robot".
**En el proyecto:** Se usa junto con Firebase Phone Auth para verificar que quien pide un OTP por SMS es un humano, no un script automatizado. Está en `firebaseOtp.js`.

### Onfido / Veriff
**¿Qué son?** Servicios externos de verificación de identidad con IA. Reciben fotos del documento y selfie, y devuelven si la persona es quien dice ser (comparación biométrica, detección de documentos falsos).
**En el proyecto:** `app/services/identity_verification.py` y `frontend/tech-registration/src/services/identityVerification.js` tienen la integración preparada para Onfido y Veriff. Actualmente funciona en modo `mock` (simulado): si se suben los tres documentos (frente, dorso, selfie), se aprueba automáticamente. Para activar Onfido en producción se necesita `ONFIDO_API_KEY` y `ONFIDO_VERIFY_ENDPOINT` en el `.env`.

### axios
**¿Qué es?** Librería JavaScript para hacer peticiones HTTP desde el navegador o Node.js. Es más cómoda que el `fetch` nativo: maneja automáticamente la serialización JSON, interceptores de errores, y tiene mejor manejo de respuestas.
**En el proyecto:** Se usa en el frontend React (`frontend/tech-registration/`) para subir archivos a Cloudinary y llamar a las APIs de Onfido/Veriff. En el backend Flask se usa `requests` (equivalente Python).

### Variables de entorno con `VITE_`
**¿Qué es?** Vite (el build tool del frontend React) expone variables de entorno al código JavaScript solo si su nombre empieza con `VITE_`. Es un mecanismo de seguridad: variables sin ese prefijo son invisibles para el navegador.
**En el proyecto:** El formulario React usa variables como `VITE_CLOUDINARY_CLOUD_NAME`, `VITE_FIREBASE_API_KEY`, `VITE_ID_PROVIDER`. Se definen en un archivo `.env` dentro de `frontend/tech-registration/`. Son distintas del `.env` del backend Flask.

### `flash()` — Mensajes de alerta de Flask
**¿Qué es?** Función de Flask que guarda un mensaje temporal en la sesión del usuario. En la siguiente petición (o en la misma respuesta), el mensaje se puede mostrar en el HTML y luego desaparece.
**En el proyecto:** Se usa en todos los blueprints para mostrar mensajes de éxito, error o aviso al usuario: `flash("Registro exitoso", "success")`, `flash("Credenciales inválidas", "danger")`. Las plantillas Jinja2 los renderizan como alertas de Bootstrap (`alert-success`, `alert-danger`, etc.).

### `url_for()` — Generador de URLs de Flask
**¿Qué es?** Función de Flask que genera la URL correcta de una ruta a partir del nombre de la función (no la URL en texto). Si la URL cambia, solo hay que cambiarla en un lugar.
**En el proyecto:** `url_for("auth.login")` genera `/auth/login`. `url_for("static", filename="css/app.css")` genera la URL correcta del archivo CSS. Se usa en plantillas Jinja2 y en redirects del backend: `return redirect(url_for("technician.dashboard"))`.

### `render_template()` — Renderizador de plantillas
**¿Qué es?** Función de Flask que toma un archivo HTML Jinja2, le inyecta variables Python, y devuelve el HTML final como respuesta HTTP.
**En el proyecto:** Cada ruta que muestra una página llama a `render_template("carpeta/pagina.html", variable=valor)`. Jinja2 reemplaza `{{ variable }}` en el HTML con el valor real.

### `redirect()` — Redirección HTTP
**¿Qué es?** Función de Flask que devuelve una respuesta HTTP 302 que le dice al navegador que vaya a otra URL.
**En el proyecto:** Se usa después de acciones importantes: después del login exitoso se redirige al dashboard, después del logout al home, después de registrarse a la pantalla de OTP.

### `UserMixin` — Interfaz de usuario para Flask-Login
**¿Qué es?** Clase de Flask-Login que le agrega a tu modelo `User` los métodos que Flask-Login necesita: `is_authenticated`, `is_active`, `is_anonymous`, `get_id()`. Sin heredarla, Flask-Login no puede gestionar la sesión del usuario.
**En el proyecto:** `class User(UserMixin, db.Model)` en `app/models.py`. Al heredar de `UserMixin`, el modelo User automáticamente tiene todos los métodos que Flask-Login espera.

### `back_populates` y `cascade` — Opciones de relaciones SQLAlchemy
**`back_populates`**: vincula dos lados de una relación bidireccional. Si `User` tiene `technician_profile` y `TechnicianProfile` tiene `user`, ambos se mantienen sincronizados en memoria. Cambiar uno actualiza el otro automáticamente.

**`cascade="all, delete-orphan"`**: cuando se borra un `User`, SQLAlchemy borra en cadena todas sus `UserSession`, `Notification`, etc. Sin esto, borrar un usuario dejaría registros huérfanos (sin padre) en la DB que causarían errores de clave foránea.

**En el proyecto:** Todas las relaciones en `models.py` usan `back_populates` para mantener la consistencia en memoria, y las relaciones hijo usan `cascade` para que el borrado en cascada funcione correctamente.

### `context_processor` — Variables globales de plantillas
**¿Qué es?** Función de Flask decorada con `@app.context_processor` que inyecta variables en el contexto de **todas** las plantillas Jinja2, sin necesidad de pasarlas en cada `render_template()`.
**En el proyecto:** Se usa para que variables como `current_user` y otras configuraciones globales estén disponibles en todos los templates automáticamente sin repetir código en cada ruta.

### `format_cop` — Filtro Jinja2 personalizado
**¿Qué es?** Un filtro de Jinja2 creado específicamente para HogarFix que formatea números como pesos colombianos.
**En el proyecto:** Definido en `app/__init__.py` y registrado con `app.jinja_env.filters["format_cop"] = format_cop`. Convierte `50000` en `$50.000`. Se usa en las plantillas de reservas y perfil técnico con `{{ precio | format_cop }}`.

### Nominatim / OpenStreetMap
**¿Qué es?** Nominatim es el geocodificador gratuito de OpenStreetMap. Convierte nombres de lugares (localidades de Bogotá) en coordenadas geográficas (latitud/longitud) y viceversa. Es la alternativa gratuita a Google Maps Geocoding API.
**En el proyecto:** Se usa como primera opción para obtener la ubicación de las localidades de los técnicos. Si Nominatim falla o no tiene el resultado, se hace fallback a Google Maps. No requiere API key (es gratuito y de código abierto).

### `localStorage` — Almacenamiento del navegador
**¿Qué es?** Espacio de almacenamiento en el propio navegador del usuario (no en el servidor). Guarda pares clave-valor de texto que persisten aunque se cierre y reabra el navegador.
**En el proyecto:** `app/static/js/help.js` usa `localStorage` para recordar si el usuario cerró el panel de Fixi. La clave `hf_mascot_hide_until` guarda hasta cuándo debe estar oculto. Cuando el usuario lo abre de nuevo, se elimina esa clave.

### `send_file()` — Envío de archivos desde Flask
**¿Qué es?** Función de Flask que envía un archivo al navegador del usuario como descarga o como recurso inline (imagen, PDF, etc.).
**En el proyecto:** Se usa en la ruta del contrato PDF: `app/blueprints/technician.py` llama a `send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="contrato.pdf")` para enviar el PDF generado en memoria (`BytesIO`) directamente al navegador sin guardarlo en disco.

### `BytesIO` — Archivo en memoria
**¿Qué es?** Objeto de Python que simula un archivo pero en memoria RAM (no en disco). Se comporta igual que un archivo abierto con `open()` pero no crea ningún archivo físico.
**En el proyecto:** `contract_pdf.py` genera el PDF de contrato en un `BytesIO`. Así el PDF se crea, se procesa y se envía al navegador sin tocar el disco. Es más rápido y no deja archivos temporales acumulándose en el servidor.

### `User-Agent`
**¿Qué es?** Cadena de texto que el navegador envía en cada petición HTTP identificándose: indica el navegador, versión y sistema operativo. Ejemplo: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/...`.
**En el proyecto:** Se captura en cada login y se guarda en `logs_login.user_agent`. Si en un login posterior el user-agent cambia (navegador diferente), el sistema envía una alerta de seguridad al correo del usuario (`send_login_alert_email`).

### LLM — Large Language Model (Modelo de Lenguaje Grande)
**¿Qué es?** Un LLM es una inteligencia artificial entrenada con cantidades masivas de texto para entender y generar lenguaje humano. No "piensa" como un humano: predice cuál es la siguiente palabra más probable en función de todo el texto que aprendió durante el entrenamiento.

**Analogía sencilla:** Imagina que leyeras todos los libros, artículos y conversaciones del mundo. Cuando alguien te hace una pregunta, sabrías responder de forma muy convincente porque has visto patrones similares miles de veces. Eso es, en esencia, lo que hace un LLM.

**Partes clave de un LLM:**
| Concepto | Qué significa |
|---|---|
| Parámetros | Números internos que el modelo ajusta durante el entrenamiento. GPT-4 tiene ~1 billón. |
| Token | Fragmento de texto (aproximadamente una sílaba o palabra corta). Los LLMs procesan tokens, no letras. |
| Contexto (context window) | Cantidad máxima de texto que el modelo puede "recordar" en una sola conversación. |
| Prompt | El texto que le envías al modelo (tu pregunta o instrucción). |
| Temperatura | Número que controla qué tan creativo o predecible es el modelo (0 = siempre igual, 1 = más variado). |
| Fine-tuning | Entrenamiento adicional del LLM con datos específicos de un dominio (ej: medicina, leyes). |

**En HogarFix:** Fixi usa la API de Groq, que ejecuta LLMs de código abierto (como LLaMA de Meta) en hardware especializado. HogarFix **no entrena** ningún LLM propio, solo lo consume como servicio externo enviando el mensaje del usuario y recibiendo la respuesta generada.

---

## 46. ¿Habría sido más fácil con otro lenguaje o stack?

Esta es una pregunta honesta y vale la pena responderla bien, porque la decisión del stack afecta todo el proyecto.

### Lo que usa HogarFix hoy

| Capa | Tecnología elegida |
|---|---|
| Lenguaje backend | Python 3 |
| Framework web | Flask 3 (micro-framework) |
| Base de datos | MySQL (vía XAMPP) |
| ORM | SQLAlchemy |
| Frontend | HTML + Jinja2 + Bootstrap 5 + JS vanilla |
| Frontend onboarding | React + Vite (solo registro técnico) |
| Chat en tiempo real | Flask-SocketIO (WebSocket) |
| IA del chatbot | Groq API (LLM externo) |
| Autenticación social | Authlib (Google OAuth) |
| PDF | fpdf2 |
| Correo | SMTP Gmail |

---

### Alternativa A — Laravel (PHP) con XAMPP
**¿Qué es Laravel?** El framework web más popular de PHP. XAMPP ya incluye PHP y Apache, así que Laravel correría sin instalar nada extra.

| Aspecto | Laravel | Flask (actual) |
|---|---|---|
| Setup inicial | `composer create-project laravel/laravel` — listo en minutos | Requiere configurar venv, instalar paquetes, crear app factory |
| Panel de administración | `php artisan make:filament-resource` o Laravel Nova (de pago) | Programado a mano en `admin.py` |
| Autenticación | `php artisan make:auth` — login/registro/recuperar contraseña generado automáticamente | Implementado a mano en `auth.py` |
| Migraciones de DB | `php artisan migrate` — versionadas y reversibles | `schema.sql` ejecutado manualmente |
| ORM | Eloquent (muy intuitivo, sintaxis limpia) | SQLAlchemy (potente pero más verboso) |
| WebSocket / Chat | Necesita Laravel Echo + Pusher o Reverb (más configuración) | Flask-SocketIO funciona directo |
| Integración IA (Groq) | Igual de fácil con HTTP client de PHP | Igual de fácil con `requests` en Python |
| XAMPP compatible | **Sí, nativamente** — Apache + PHP ya están ahí | Corre por separado (puerto 5000) |

**Veredicto:** Dado que ya se usa XAMPP, Laravel habría sido la elección **más natural** para este entorno. El scaffolding automático de auth, migraciones y panel admin habría ahorrado días de trabajo. La curva de aprendizaje de PHP es similar a Python.

---

### Alternativa B — Django (Python)
**¿Qué es Django?** El framework web "baterías incluidas" de Python. Mismo lenguaje, mucho más automatizado.

| Aspecto | Django | Flask (actual) |
|---|---|---|
| Panel de administración | `/admin` generado automáticamente con los modelos | Hecho a mano |
| Autenticación | `django.contrib.auth` — login, grupos, permisos ya hechos | Implementado con Flask-Login manualmente |
| Migraciones | `makemigrations` + `migrate` — automáticas y versionadas | `schema.sql` ejecutado a mano |
| ORM | Django ORM — más simple para relaciones comunes | SQLAlchemy — más flexible pero más verboso |
| Formularios con validación | `django.forms` — generación automática | WTForms / validación manual |
| WebSocket / Chat | Django Channels (añade complejidad) | Flask-SocketIO más simple |
| Curva de aprendizaje | Mayor ("hace magia" que hay que entender) | Menor (explícito, ves todo) |

**Veredicto:** Para un equipo que ya sabe Python, Django habría acelerado la parte de auth y admin significativamente. El panel `/admin` de Django habría reemplazado todo `blueprints/admin.py` y `templates/admin/` de un solo golpe. La desventaja: Django "impone" su forma de hacer las cosas, lo que puede ser frustrante cuando quieres salirte del camino estándar.

---

### Alternativa C — Node.js + Express (JavaScript en el servidor)
**¿Qué es Express?** El framework web minimalista de Node.js. Mismo lenguaje que el navegador (JavaScript) tanto en frontend como backend.

| Aspecto | Node.js + Express | Flask (actual) |
|---|---|---|
| WebSocket / Chat | **Nativo** — Node.js es asíncrono por diseño, Socket.IO nació aquí | Flask-SocketIO funciona, pero Flask es síncrono por naturaleza |
| Un solo lenguaje | JavaScript en front y back (menos contexto mental) | Python en back, JS en front (dos lenguajes) |
| NPM ecosystem | Enorme, especialmente para frontend | Pip también es enorme para backend |
| ORM | Prisma, Sequelize, TypeORM | SQLAlchemy |
| Templates HTML | EJS, Pug (similar a Jinja2) | Jinja2 |
| Integración IA (Groq) | Igual de fácil con `fetch` o `axios` | Igual con `requests` |
| Rendimiento | Muy alto en operaciones I/O (ideal para chat) | Adecuado para carga actual |

**Veredicto:** Para el chat en tiempo real de Fixi, Node.js habría sido la elección más eficiente técnicamente (Socket.IO nació ahí). Pero cambiar todo el backend a JS solo por el chat no justifica el costo. Flask-SocketIO funciona bien para la escala actual.

---

### Alternativa D — Next.js + Supabase (el atajo moderno)
**¿Qué es?** Next.js es un framework React con servidor integrado. Supabase es un "Firebase de código abierto": da base de datos PostgreSQL, autenticación, almacenamiento de archivos y API REST automática, todo como servicio en la nube.

| Aspecto | Next.js + Supabase | Flask + MySQL (actual) |
|---|---|---|
| Auth (login, registro, OTP, OAuth) | Supabase Auth — **ya hecho**, solo configurar | Implementado desde cero (semanas de trabajo) |
| Base de datos | PostgreSQL en la nube, accesible con URL | MySQL local en XAMPP |
| Almacenamiento de fotos | Supabase Storage — bucket en la nube | `app/static/uploads/` en disco local |
| API REST automática | Supabase genera la API de cada tabla sola | Cada ruta programada a mano en blueprints |
| Chat en tiempo real | Supabase Realtime — suscripciones a tablas en tiempo real | Flask-SocketIO + Groq |
| Despliegue | Vercel (un clic para Next.js) + Supabase gratuito | Servidor propio o VPS |
| Costo | Gratis hasta límites generosos | Gratis (local), pero requiere servidor propio en producción |
| Requiere internet para desarrollar | **Sí** — Supabase es en la nube | **No** — todo local con XAMPP |
| Curva de aprendizaje | Alta (React, TypeScript, Next.js, Supabase API) | Media (Python, Flask, SQL) |

**Veredicto:** Este stack habría sido el más rápido para llegar a un MVP funcional con autenticación, almacenamiento y base de datos sin escribir casi nada de backend. La contrapartida: dependes de servicios externos desde el día uno, y la curva de aprendizaje de React + TypeScript + Next.js es considerable si no se conoce.

---

### El veredicto honesto

> **¿Fue la mejor elección? Sí, para el contexto de este proyecto.**

| Criterio | Ganador |
|---|---|
| Más rápido de arrancar dado que usas XAMPP | Laravel |
| Más automatizado en Python | Django |
| Más natural para el chat en tiempo real | Node.js + Express |
| MVP más rápido sin escribir backend | Next.js + Supabase |
| Mejor para aprender cómo funciona todo por dentro | **Flask (lo que se eligió)** |
| Más flexible y sin magia oculta | **Flask (lo que se eligió)** |
| Más fácil de integrar con Groq y APIs de IA en Python | **Flask (lo que se eligió)** |

Flask obliga a construir cada pieza a mano (auth, OTP, admin, ORM, PDF, WebSocket). Eso es una desventaja en tiempo de desarrollo, pero una **ventaja enorme en comprensión**: quien construyó HogarFix sabe exactamente cómo funciona cada parte porque la programó. Eso no pasa con Django o Supabase, donde gran parte del sistema es una caja negra.

Para una versión 2 en producción real, la recomendación sería:
- Migrar la base de datos de MySQL a **PostgreSQL** (más robusto, mejor soporte en la nube).
- Añadir **Supabase Storage** o **Cloudinary** para las fotos (fuera del disco local).
- Considerar **Celery + Redis** para tareas asíncronas (envío de correos, notificaciones en segundo plano).
- Desplegar en **Railway, Render o un VPS** con Gunicorn + Nginx.

---

## 47. Estado actual del proyecto y roadmap — qué falta para producción

> Este repositorio es una **versión MVP de prueba / portafolio**. No está en producción ni conectado a pagos reales. La siguiente sección documenta qué funcionalidades faltan para poder lanzarlo al mercado.

---

### ✅ Lo que ya funciona (completo en esta versión)

| Área | Detalle |
|---|---|
| Autenticación completa | Registro, login, OTP por email, recuperar contraseña, Google OAuth, Microsoft OAuth, 2FA |
| Panel administrador | Dashboard, lista de usuarios, detalle usuario/técnico, reservas, reseñas, anuncios CRUD, verificación y suscripciones manuales |
| Panel técnico | Dashboard con calendario-agenda, perfil, fotos de trabajo, disponibilidad, settings, notificaciones internas, descarga de contrato PDF |
| Panel cliente | Dashboard, historial de reservas, búsqueda de técnicos, perfil, settings, notificaciones internas, repetir servicio |
| Sistema de reservas | Crear, confirmar (técnico), completar con evidencia fotográfica, cancelar, liberar slot, reseñas con calificación |
| Comprobantes de pago | Subida de foto del comprobante (Nequi, Daviplata, transferencia), confirmación manual de efectivo |
| Suscripciones del técnico | Planes Básico / Profesional / Elite con límites de reservas — modo sandbox (sin cobro real) |
| Chat Fixi (IA) | Chatbot con Groq (LLM) + fallback a FAQ local en español |
| Contratos PDF | Generación automática del contrato de prestación de servicios |
| Emails automáticos | Bienvenida, alerta de login nuevo, OTP, recuperar contraseña (SMTP Gmail/Mailtrap) |
| Anuncios modales | Admin crea/edita/desactiva anuncios que aparecen al entrar al sitio |
| Páginas legales | Términos y condiciones, política de privacidad, política de cancelación |
| Páginas de error | 403, 404, 500, 503 con diseño propio |
| Seguridad básica | CSRF (Flask-WTF), rate limiting en login/registro, bcrypt, headers de seguridad |
| Internacionalización | Sistema de traducciones JS (español/inglés) en settings del usuario |

---

### 🔴 Crítico — necesario antes de lanzar al mercado

Estas funcionalidades son **bloqueadoras de producción**: sin ellas el negocio no puede operar.

#### 1. Pasarela de pago real
- **Qué falta:** PSE, Nequi y Daviplata existen solo en la interfaz. No hay integración real con ninguna pasarela de pago colombiana.
- **Impacto:** Los clientes no pueden pagar en línea. Los técnicos no pueden pagar su suscripción.
- **Cómo resolverlo:** Integrar **Wompi** (Bancolombia), **PayU Colombia** o **ePlacetoPay**. Wompi es el más sencillo para MVP.
- **Archivos a modificar:** `app/blueprints/booking.py`, `app/blueprints/technician.py` (activate_subscription), nuevo blueprint `payments.py`.

#### 2. Email de notificación al técnico cuando llega una reserva
- **Qué falta:** Al crear una reserva, el técnico recibe una notificación interna (badge) pero **no recibe email**. Si no tiene la app abierta, no se entera.
- **Impacto:** Los técnicos pierden solicitudes de trabajo.
- **Cómo resolverlo:** En `booking.py → create_booking()`, llamar a `send_email()` con los datos de la reserva al correo del técnico.
- **Archivos a modificar:** `app/blueprints/booking.py`, `app/services/email.py`.

#### 3. Notificaciones push en tiempo real (WebSocket)
- **Qué falta:** El badge de notificaciones solo se actualiza al recargar la página. `socket.io.min.js` está en los estáticos pero no se usa para push de notificaciones.
- **Impacto:** El técnico no sabe en tiempo real que un cliente confirmó pago o que llegó una reserva nueva.
- **Cómo resolverlo:** Activar Flask-SocketIO en el servidor y emitir eventos en los puntos clave (nueva reserva, cambio de estado, pago confirmado).
- **Archivos a modificar:** `app/__init__.py`, `app/extensions.py`, `app/blueprints/booking.py`, todos los templates base.

#### 4. Verificación de identidad real (cédula)
- **Qué falta:** El sistema tiene el flujo completo (webhook en `api.py → identity_webhook`) pero el provider configurado es **mock** — aprueba automáticamente sin verificar nada real.
- **Impacto:** Cualquiera puede registrarse como técnico sin verificar su identidad.
- **Cómo resolverlo:** Integrar **Onfido**, **Veriff** o **MetaMap** (este último opera bien en Colombia).
- **Archivos a modificar:** `app/services/identity_verification.py`, variables `.env` (API keys del provider).

#### 5. Firma del representante legal en contratos PDF
- **Qué falta:** El archivo `app/static/img/firma-representante-legal.png` **no existe**. Los contratos PDF se generan sin la firma del administrador/empresa.
- **Impacto:** El contrato no tiene validez visual/formal.
- **Cómo resolverlo:** El administrador debe crear o escanear su firma, guardarla como PNG en esa ruta, o configurar una ruta para subirla desde el panel admin.

---

### 🟡 Importante — mejora significativa la experiencia

Estas funcionalidades no bloquean el lanzamiento pero son necesarias para que los usuarios vuelvan.

#### 6. Filtros avanzados en búsqueda de técnicos
- **Qué falta:** La búsqueda actual filtra por especialidad y localidad. No hay filtro por precio, calificación mínima, día disponible o tipo de técnico.
- **Archivos a modificar:** `app/blueprints/main.py → search_technicians()`, `app/templates/main/search.html`.

#### 7. Perfil público del técnico (URL compartible)
- **Qué falta:** No existe una página `/tecnico/<slug>` que el técnico pueda compartir en redes sociales o WhatsApp para que los clientes reserven sin necesidad de registrarse primero.
- **Archivos a crear:** Nueva ruta en `main.py` o `technician.py`, nuevo template `technician/public_profile.html`.

#### 8. Panel de ingresos del técnico
- **Qué falta:** El técnico no puede ver cuánto ha cobrado, cuántas reservas completó por mes ni su historial financiero.
- **Archivos a crear/modificar:** Nueva ruta en `technician.py`, nuevo template `technician/earnings.html`.

#### 9. Chat directo cliente ↔ técnico
- **Qué falta:** El `chat.py` actual es solo el chatbot Fixi (IA). No existe mensajería directa entre cliente y técnico dentro de una reserva.
- **Impacto:** El cliente y el técnico coordinan por WhatsApp fuera de la plataforma, lo que reduce el control de la plataforma sobre la transacción.
- **Cómo resolverlo:** Agregar un modelo `Message` (booking_id, sender_id, content, timestamp) y una vista de chat por reserva usando Flask-SocketIO.

#### 10. Reportes y estadísticas para el administrador
- **Qué falta:** El admin solo ve KPIs básicos en el dashboard. No hay exportación de datos, gráficas de ingresos, técnicos más activos, servicios más pedidos ni tendencias.
- **Archivos a crear:** Nueva ruta `admin/reports`, template `admin/reports.html`, posiblemente con Chart.js.

#### 11. Gestión de comprobantes de pago desde admin
- **Qué falta:** El admin no tiene una vista centralizada para revisar y aprobar los comprobantes de pago subidos por los clientes.
- **Archivos a modificar:** `app/blueprints/admin.py`, nuevo template `admin/pagos.html`.

---

### 🟢 Deseables — para una versión 2 robusta

Estas funcionalidades mejoran la plataforma pero pueden esperar al siguiente ciclo de desarrollo.

| # | Funcionalidad | Descripción |
|---|---|---|
| 12 | Fotos en reseñas | El cliente puede adjuntar hasta 3 fotos al dejar una reseña del servicio |
| 13 | SMS además de email | Notificaciones por SMS al técnico y cliente (Twilio o AWS SNS) |
| 14 | Calendario exportable (iCal) | El técnico puede exportar su agenda a Google Calendar / Apple Calendar |
| 15 | Códigos de descuento | Admin crea cupones de descuento para las suscripciones o servicios |
| 16 | Sistema de referidos | Un cliente que refiere a otro obtiene descuento en su próxima reserva |
| 17 | Búsqueda por geolocalización | Ordenar técnicos por distancia usando la ubicación del cliente |
| 18 | Sistema de disputas | El cliente puede abrir una disputa si el servicio no fue satisfactorio |
| 19 | SEO / meta tags | Agregar `<meta description>` y Open Graph tags para compartir en redes sociales |
| 20 | Almacenamiento en la nube | Mover las fotos de `app/static/uploads/` a Cloudinary o Supabase Storage |
| 21 | Despliegue en servidor | Configurar Gunicorn + Nginx en Railway, Render o VPS para que sea accesible en internet |
| 22 | PostgreSQL en producción | Migrar de MySQL (XAMPP local) a PostgreSQL (más robusto, mejor soporte en la nube) |
| 23 | Tareas asíncronas (Celery) | Envío de emails en segundo plano para no bloquear la respuesta del servidor |

---

### Resumen de prioridades

```
ANTES DE LANZAR (crítico):
  [ ] Pasarela de pago real (Wompi / PayU)
  [ ] Email al técnico cuando llega una reserva
  [ ] Notificaciones push en tiempo real (WebSocket)
  [ ] Verificación de identidad real (Onfido / MetaMap)
  [ ] Firma representante legal PNG (archivo físico)

PRIMERA SEMANA EN PRODUCCIÓN (importante):
  [ ] Filtros avanzados en búsqueda
  [ ] Perfil público del técnico
  [ ] Panel de ingresos del técnico
  [ ] Chat cliente ↔ técnico por reserva
  [ ] Reportes admin (exportación + gráficas)
  [ ] Vista de comprobantes de pago en admin

VERSIÓN 2 (deseables):
  [ ] Fotos en reseñas
  [ ] SMS (Twilio)
  [ ] Calendario iCal
  [ ] Códigos de descuento / referidos
  [ ] Geolocalización en búsqueda
  [ ] Sistema de disputas
  [ ] Migrar a PostgreSQL + Cloudinary + VPS
```
