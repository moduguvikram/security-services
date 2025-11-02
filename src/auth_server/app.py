import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector, current_token
from authlib.integrations.sqla_oauth2 import create_query_client_func, create_save_token_func, create_bearer_token_validator
from werkzeug.security import gen_salt
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode

try:
    from .models import db, User, OAuth2Client, OAuth2Token
except ImportError:
    from models import db, User, OAuth2Client, OAuth2Token

from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6750 import BearerTokenValidator

# Disable HTTPS check for production (Railway handles SSL at proxy)
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(
    __name__,
    instance_path='/tmp',
    instance_relative_config=True
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:////tmp/dev.db")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-change-me")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["OAUTH2_REFRESH_TOKEN_GENERATOR"] = True
app.config["OAUTH2_TOKEN_EXPIRES_IN"] = {"authorization_code": 864000, "implicit": 3600, "password": 864000, "client_credentials": 864000}
db.init_app(app)

class MyBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        return OAuth2Token.query.filter_by(access_token=token_string).first()

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return getattr(token, "revoked", False)



with app.app_context():
    db.create_all()

# Swagger UI setup
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "OAuth2 Server with OTP",
        'tryItOutEnabled': True
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    return jsonify({
        "message": "OAuth2 Server with OTP Authentication",
        "version": "1.0.0",
        "documentation": f"{request.host_url}docs",
        "endpoints": {
            "register_user": "/register_user",
            "verify_otp": "/verify_otp",
            "qr_code": "/qr_code/<username>",
            "create_client": "/create_client",
            "token": "/token",
            "profile": "/profile"
        }
    })

@app.route('/static/swagger.json')
def swagger_spec():
    return send_file(os.path.join(os.path.dirname(__file__), 'swagger.json'))

# OAuth2 setup
query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization = AuthorizationServer(app, query_client=query_client, save_token=save_token)

# OAuth2 bearer validator
require_oauth = ResourceProtector()
# bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
# require_oauth.register_token_validator(bearer_cls())
require_oauth.register_token_validator(MyBearerTokenValidator())
# ------------------------------------------------------------
#  OTP (OATH) + User registration
# ------------------------------------------------------------

@app.route("/register_user", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify(error="Username and password are required"), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify(error="User already exists"), 400

    otp_secret = pyotp.random_base32()
    user = User(
        username=username,
        password=generate_password_hash(password),
        otp_secret=otp_secret
    )
    db.session.add(user)
    db.session.commit()

    otp_uri = pyotp.TOTP(otp_secret).provisioning_uri(
        name=username, issuer_name="ThisOAuthServer"
    )
    
    qr_code_url = f"{request.host_url}qr_code/{username}"
    
    return jsonify(message="User registered", otp_uri=otp_uri, qr_code_url=qr_code_url)

@app.route("/qr_code/<username>")
def get_qr_code(username):
    user = User.query.filter_by(username=username).first()
    if not user or not user.otp_secret:
        return jsonify(error="User not found"), 404
    
    otp_uri = pyotp.TOTP(user.otp_secret).provisioning_uri(
        name=username, issuer_name="ThisOAuthServer"
    )
    img = qrcode.make(otp_uri)
    
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')

@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.json
    username = data.get("username")
    code = data.get("code")
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify(error="User not found"), 404

    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(code):
        user.otp_verified = True
        db.session.commit()
        return jsonify(valid=True)
    return jsonify(valid=False), 401

# ------------------------------------------------------------
#  OAuth2 Client Management
# ------------------------------------------------------------

@app.route("/create_client", methods=["POST"])
def create_client():
    data = request.json
    client_name = data.get("client_name")
    redirect_uri = data.get("redirect_uri")
    grant_types = data.get("grant_types", ["client_credentials", "authorization_code", "password"])
    scope = data.get("scope", "profile email")
    
    if not client_name or not redirect_uri:
        return jsonify(error="Client name and redirect URI are required"), 400

    # Check if client name already exists
    existing = OAuth2Client.query.filter_by(client_name=client_name).first()
    if existing:
        return jsonify(error="Client name already exists"), 400

    client_id = gen_salt(24)
    client_secret = gen_salt(48)
    
    client_metadata = {
        "client_name": client_name,
        "client_uri": redirect_uri,
        "grant_types": grant_types,
        "response_types": ["code"],
        "redirect_uris": [redirect_uri],
        "scope": scope,
    }
    
    client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        client_name=client_name
    )
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    
    return jsonify(client_id=client_id, client_secret=client_secret)

# ------------------------------------------------------------
#  OAuth2 Token Endpoint
# ------------------------------------------------------------

from authlib.oauth2.rfc6749 import grants

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.otp_verified:
            return user
        return None

authorization.register_grant(PasswordGrant)
authorization.register_grant(grants.ClientCredentialsGrant)
authorization.register_grant(grants.RefreshTokenGrant)

@app.route("/token", methods=["POST"])
def issue_token():
    return authorization.create_token_response()

# ------------------------------------------------------------
#  Protected Resource Example
# ------------------------------------------------------------





@app.route("/profile")
@require_oauth()#"profile"
def profile():
    token = current_token
    # If the token belongs to a user (resource owner)
    if hasattr(token, "user") and token.user:
        return jsonify({
            "type": "user",
            "username": token.user.username,
            "otp_verified": getattr(token.user, "otp_verified", False)
        })
   
    return jsonify({"type": "client",  "client_id": token.client_id, "message": "Machine token access"})

# ------------------------------------------------------------
#  HTTPS for local testing
# ------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    if debug:
        app.run(debug=True, ssl_context="adhoc", port=port)
    else:
        app.run(host="0.0.0.0", port=port, debug=False)
