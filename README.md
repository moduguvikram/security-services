
# OAuth2 Server with OTP Authentication

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A production-ready OAuth2 authorization server with Time-based One-Time Password (TOTP) authentication built with Flask and Authlib.

## Features

- 🔐 OAuth2 Authorization Server (RFC 6749)
- 🔑 TOTP/OTP Authentication (Google Authenticator compatible)
- 🎫 Multiple Grant Types: Password, Client Credentials, Refresh Token
- 🛡️ Secure token management
- 📱 QR Code generation for OTP setup
- 🚀 Railway deployment ready
- 💾 SQLite/PostgreSQL support

## Prerequisites

- Python 3.9+
- Poetry Package Manager

## Installation

```bash
# Clone the repository
git clone https://github.com/moduguvikram/security-services.git
cd security-services

# Install dependencies
poetry install

# Configure environment (optional)
cp .env.example .env
# Edit .env with your settings
```

## Quick Start

### Local Development

```bash
# Set development mode
export FLASK_ENV=development

# Run the server (with HTTPS)
poetry run python3 src/auth_server/app.py
```

Server runs at: `https://127.0.0.1:5000`

### Production Deployment

See [Deployment Guide](#deployment) below. 


## API Documentation

### 1. Register a User

curl -X POST https://127.0.0.1:5000/register_user -H "Content-Type: application/json" -d '{"username":"testUser","password":"testPassowrd123"}' -k

{
    "message": "User registered",
    "otp_uri": "otpauth://totp/ThisOAuthServer:testUser?secret=IFQVWCP4GKTPAOULY2IIIZQULZA4ZRL7&issuer=ThisOAuthServer",
    "qr_code": "iVBORw0KGgoAAAANSUhEUgAAAeoAAAHqAQAAAADjFjCXAAAEN0lEQVR4nO2dUaqsOBCG/xqFfowwC3ApcWeHu6S7A7MUF3AhPjZEah5SifHAMNA69Gn866Exth9poUglf1XSojhh4a8zNECcOHHixIkTJ078WlzMeogMmwBrD5nyF33+AFYRmdby6HRd78TvhkNVVeFVVTV2qhqBvWmPHO41xPzR70783fhahq8wJiCIiMiwSXa9MKoiDFt+xIa+K3snfi+8/9YWOAB+3nrA/ekFLkHgtl4BqFzcO3HiZp3qDEBnAPBxE51hU79873/tnfiNcKdqbrb0QBgA+Voeqr+GToH1oYBLkAmAqqaLeyd+L9wibMixs8st8csjR1PxS5/Ex78B//uhAmyHKPvR7078XXj2uiYtFgaYX4UxQcP4FMAlaBg6AO6YQfvodyf+LrxRTuAjAB+7HE3LvaKmNOaonBA/ZVl+q4qceRNMllPVVNcVXXFCNZ+k1xF/zbJrzQCyNteOcJ3q7BLy0AccRj16HfHXrY2wmrA7XA6k+ZFoQoq5qEvl6qPfnfi78BphLfuVXQ+uxFUUD8viisZDDo1eR/x1XGR8ijnSamKKfGmC6vJQmVYTiGUCINPKjBjxM2b+42cosA65pVj7qqZUgW7tk2K1e3pJ78TvidfVRFcLTwAgN/dYe6g+qboKIyzx18xmabG0/Z7uQqc61yVFdj2XwNUE8Wu8DnWsm4sEbGJwVVOaVC31OuLnrNHrcpiNANBcWbpfZ2dr3V3Xo9cRf81qDqLRRuyqDH2ml9TSYkZY4lfgMgGAX8TWq34p2oiPgMhgHzbNWx96wE/2TvxueJ3X2RhmJQCa8G3fBCMs8cvwdg1bHW6PsNn/ZqAWo+xf0OuIv2q7XlfMBjxbYZQRLj88V6mO8zriJ3H5ipuUnWH1O5fyDE9krIUnaw+dsXE/LPEzto9wVtWEXUOxSqd9hDNP5LyO+Dk7CCRWQdfGVZewV5qUcicqJ8QvwTcB3FMQxgT5ioBMrs2NIeS9150iDJf3TvxWeJMRa5L8c8l+leBa17Wx7ExkhCX+sjV7/wUuAkCXBBAo3J9efIQiSK5+SgJ0Sfzv4aLeid8ZV42bqO65iSyVlGhqdSibqMYtB+Ereyd+Y1xk1Lo955mPE1Nd+pIRG1M+FKA5j+Ln/Hjin4QfMmKloM7y+xGNmmLKSbniGpb4CdOjlWhaq+pQRLuaB2MtMfFrchP1rE7kba/6FP01bAKvVUiBHeIJv7DmhPgFeA6aEci+FuSRC5p0XuVwnI5L4GqC+DXzuv2IEytyqs1YVw5Fzdv3yDLCEr8E37e92kK2WU1UqXh5qD3ys3488Q/Bv58QizABJefVqQQBxMcBGvZI657l+qPfnfi78ZICazbABumxCyml8ElsSXFp78TvhTd6Hb5vT4y15qnes6PrOK8jfsZE//uZfzf+ex1x4sSJEydOnPhPwf8BloTqA/S/4FsAAAAASUVORK5CYII="
}

Response gives you an otp_uri and an qr_code in base64 encoded string.
Scan it in Google Authenticator or any other Authenticator.


Verify OTP:

curl -X POST https://127.0.0.1:5000/verify_otp \
  -H "Content-Type: application/json" \
  -d '{"username":"testUser","code":"056628"}' -k

  Response:

curl -X POST https://127.0.0.1:5000/verify_otp \
  -H "Content-Type: application/json" \
  -d '{"username":"testUser","code":"091204"}' -k
{
  "valid": true
}


Create an OAuth2 client


curl -X POST https://127.0.0.1:5000/create_client \
  -H "Content-Type: application/json" \
  -d '{"client_name":"RestServicesClient","redirect_uri":"https://127.0.0.1:5000/callback"}' -k

{
  "client_id": "4R0o9atlUvUvAWhNNihPSsLN",
  "client_secret": "J3oq2uHDGdJQbz7zlwjOSnECYqplEXj34eH3SCOzK0liV4kO"
}

  Note down client_id and client_secret.



Get a token using password grant (requires verified OTP)

curl -X POST https://127.0.0.1:5000/token  -u "4R0o9atlUvUvAWhNNihPSsLN:J3oq2uHDGdJQbz7zlwjOSnECYqplEXj34eH3SCOzK0liV4kO" -d "grant_type=password&username=testUser&password=testPassword123" -k


{"access_token": "MTV3IBXhMhrs6RnKAx6jJ0wgXZN1ooq5pbXHI7F2YE", "expires_in": 864000, "refresh_token": "g67yHraHSKeShhelY8VVjfcjEDwx9iAbAcBbdno1nDvsV5KU", "token_type": "Bearer"}%                  


### 4. Client Credentials Grant

For machine-to-machine authentication:

curl -X POST https://127.0.0.1:5000/create_client -H "Content-Type: application/json" -d '{"client_name":"ServiceApp","redirect_uri":"https://localhost/callback"}' -k
{
  "client_id": "fZ4AqsZFTgMNvfIzaCPutJuB",
  "client_secret": "F7N6SSm2ipEQOrfwEThDfbzW1R0kia5qy55ZR77ofsvJnEaC"
}

Save the returned client_id and client_secret.

curl -X POST https://127.0.0.1:5000/token -u "jxBm4BIM4WFIHi0ZsiUlG5W4:eMtqnmtNQVlw5RA4N3GGqQSPrfdcEfH2oGTT9ppQ1MWj25q9"  -d "grant_type=client_credentials&scope=profile" -k

{"access_token": "GPSlmILLMF3W1GMNyVqJN4GSnwmuiKr02zbT4iaZ1f", "expires_in": 864000, "scope": "profile", "token_type": "Bearer"}%

curl https://127.0.0.1:5000/profile  -H "Authorization: Bearer N2KproeimHJ3J4Kum2OBVVZhWZqqf62O8dsPtjtITh" -k

## Deployment

### Railway

1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables:
   - `SECRET_KEY`: Random secret string
   - Optional: Add PostgreSQL database
4. Deploy automatically

### Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: Flask secret key (required for production)
- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Set to `development` for local dev

## Security Considerations

- Always use HTTPS in production
- Set a strong `SECRET_KEY`
- Use PostgreSQL for production (not SQLite)
- Implement rate limiting for production
- Review token expiration settings

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

Create an issue on GitHub for bugs or feature requests.