import sys
import os
from flask import Flask, request, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector, current_token
from authlib.integrations.sqla_oauth2 import create_query_client_func, create_save_token_func, create_bearer_token_validator
from werkzeug.security import gen_salt
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, OAuth2Client, OAuth2Token
import pyotp
import qrcode

from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6750 import BearerTokenValidator

app = Flask(
    __name__,
    instance_path='/tmp',
    instance_relative_config=True
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:////tmp/dev.db")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-change-me")
app.config["OAUTH2_REFRESH_TOKEN_GENERATOR"] = True
db.init_app(app)

class MyBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        return OAuth2Token.query.filter_by(access_token=token_string).first()

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return getattr(token, "revoked", False)



with app.app_context():
    db.drop_all()
    db.create_all()

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
    img = qrcode.make(otp_uri)
    filename = f"{username}_otp.png"
    path = os.path.join("static/qrcodes", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

    print(otp_uri)
    return jsonify(message="User registered", otp_uri=otp_uri)

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

    client_id = gen_salt(24)
    client_secret = gen_salt(48)
    client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        
    )
    client_metadata={
            "client_name": client_name,
            "client_uri": redirect_uri,
            "grant_types": ["client_credentials", "authorization_code", "password"],
            "response_types": ["code"],
            "redirect_uris": [redirect_uri],
            "scope": "profile email",
        }
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
