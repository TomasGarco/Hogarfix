from app import create_app
from app.extensions import socketio
from app.utils import send_email
import click

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)


@app.cli.command("mail-test")
@click.option("--to", required=True, help="Correo destino para la prueba SMTP.")
def mail_test(to):
    ok, status = send_email(
        subject="Prueba SMTP HogarFix",
        to_email=to,
        text_body="Este es un correo de prueba enviado desde HogarFix.",
        html_body="<p>Este es un correo de <strong>prueba</strong> enviado desde HogarFix.</p>",
    )

    if ok:
        print("Correo de prueba enviado correctamente.")
        return

    print(f"No se pudo enviar el correo. Estado: {status}")
    raise SystemExit(1)



# --- DEV ONLY: Endpoint para ver el último enlace o PIN enviado por correo ---
import os
from flask import Response

def add_dev_mail_endpoint(app):
    if app.config.get("ENV") == "development":
        @app.route("/dev/last-mail")
        def dev_last_mail():
            mail_path = os.environ.get("MAIL_FILE_PATH") or app.config.get("MAIL_FILE_PATH") or "app/mail_outbox.log"
            if not os.path.exists(mail_path):
                return "No se encontró mail_outbox.log", 404
            with open(mail_path, encoding="utf-8") as f:
                content = f.read()[-4000:]  # Solo los últimos 4000 caracteres
            # Busca el último enlace http o PIN en el texto
            import re
            links = re.findall(r"https?://[\w\-.:/?=&%]+", content)
            pins = re.findall(r"\b\d{4,8}\b", content)
            html = "<h2>Último enlace enviado:</h2>"
            if links:
                html += f'<a href="{links[-1]}">{links[-1]}</a><br><br>'
            else:
                html += "No se encontró enlace.<br>"
            if pins:
                html += f"<b>Último PIN detectado:</b> {pins[-1]}<br><br>"
            html += "<pre style='white-space:pre-wrap;background:#eee;padding:1em'>" + content + "</pre>"
            html += "<hr><small>Este endpoint es solo para pruebas locales. Elimínalo en producción.</small>"
            return Response(html, mimetype="text/html")

    return app

if __name__ == "__main__":
    app = add_dev_mail_endpoint(app)
    app.run(debug=True)
