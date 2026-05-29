from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

try:
	from authlib.integrations.flask_client import OAuth
except ModuleNotFoundError:
	OAuth = None


db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
oauth = OAuth() if OAuth is not None else None
oauth_available = oauth is not None
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para continuar."
login_manager.login_message_category = "warning"
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=[],  # sin límite global; aplicamos por ruta
)
