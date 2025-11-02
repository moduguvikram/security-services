from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin, OAuth2TokenMixin
from sqlalchemy import Column, Integer, String

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    def get_user_id(self):
        return self.id

class OAuth2Client(db.Model, OAuth2ClientMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(48), unique=True, nullable=False)
    client_secret = db.Column(db.String(120), nullable=False)
    client_id_issued_at = db.Column(db.Integer, nullable=False, default=0)
    client_secret_expires_at = db.Column(db.Integer, nullable=False, default=0)

class OAuth2Token(db.Model, OAuth2TokenMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')