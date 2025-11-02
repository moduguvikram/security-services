# OAuth2 Server with OTP Authentication

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An OAuth2 authorization server with Time-based One-Time Password (TOTP) authentication built with Flask and Authlib.

## Live Demo

🌐 **API Documentation:** https://web-production-7a862.up.railway.app/docs/

Try the interactive API documentation and test all endpoints directly in your browser.

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

Server runs at: `https://127.0.0.1:5001`

### Production Deployment

See [Deployment Guide](#deployment) below.

## API Documentation

**Interactive Documentation:** https://web-production-7a862.up.railway.app/docs/

All examples below use local development URLs. Replace `https://127.0.0.1:5001` with `https://web-production-7a862.up.railway.app` for production.

### 1. Register a User

Register a new user and get OTP setup information.

```bash
curl -X POST https://127.0.0.1:5000/register_user \
  -H "Content-Type: application/json" \
  -d '{"username":"testUser","password":"testPassword123"}' -k
```

**Response:**
```json
{
  "message": "User registered",
  "otp_uri": "otpauth://totp/ThiaOAuthServer:testUser?secret=ABCD1234...",
  "qr_code_url": "https://127.0.0.1:5000/qr_code/testUser"
}
```

### 2. Get QR Code Image

Retrieve the QR code as a PNG image.

```bash
curl https://127.0.0.1:5000/qr_code/testUser -k > qr_code.png
```

Or open in browser: `https://127.0.0.1:5000/qr_code/testUser`

Scan the QR code in Google Authenticator or any TOTP authenticator app.

### 3. Verify OTP

Verify the OTP code from authenticator app.

```bash
curl -X POST https://127.0.0.1:5000/verify_otp \
  -H "Content-Type: application/json" \
  -d '{"username":"testUser","code":"123456"}' -k
```

**Response:**
```json
{
  "valid": true
}
```

### 4. Create OAuth2 Client

Create a new OAuth2 client application.

```bash
curl -X POST https://127.0.0.1:5000/create_client \
  -H "Content-Type: application/json" \
  -d '{"client_name":"MyApp","redirect_uri":"https://127.0.0.1:5000/callback"}' -k
```

**Optional parameters:**
- `grant_types`: Array of grant types (default: `["client_credentials", "authorization_code", "password"]`)
- `scope`: Space-separated scopes (default: `"profile email"`)

**Response:**
```json
{
  "client_id": "4R0o9atlUvUvAWhNNihPSsLN",
  "client_secret": "J3oq2uHDGdJQbz7zlwjOSnECYqplEXj34eH3SCOzK0liV4kO"
}
```

Save the `client_id` and `client_secret`.

### 5. Get Token - Password Grant

Get an access token using user credentials (requires verified OTP).

```bash
curl -X POST https://127.0.0.1:5000/token \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=password&username=testUser&password=testPassword123" -k
```

**Response:**
```json
{
  "access_token": "MTV3IBXhMhrs6RnKAx6jJ0wgXZN1ooq5pbXHI7F2YE",
  "expires_in": 864000,
  "refresh_token": "g67yHraHSKeShhelY8VVjfcjEDwx9iAbAcBbdno1nDvsV5KU",
  "token_type": "Bearer"
}
```

### 6. Get Token - Client Credentials Grant

Get an access token for machine-to-machine authentication.

```bash
curl -X POST https://127.0.0.1:5000/token \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=client_credentials&scope=profile" -k
```

**Response:**
```json
{
  "access_token": "GPSlmILLMF3W1GMNyVqJN4GSnwmuiKr02zbT4iaZ1f",
  "expires_in": 864000,
  "scope": "profile",
  "token_type": "Bearer"
}
```

### 7. Get Token - Refresh Token Grant

Refresh an expired access token.

```bash
curl -X POST https://127.0.0.1:5000/token \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=refresh_token&refresh_token=REFRESH_TOKEN" -k
```

### 8. Access Protected Resource

Access a protected endpoint using the access token.

```bash
curl https://127.0.0.1:5000/profile \
  -H "Authorization: Bearer ACCESS_TOKEN" -k
```

**Response (User token):**
```json
{
  "type": "user",
  "username": "testUser",
  "otp_verified": true
}
```

**Response (Client token):**
```json
{
  "type": "client",
  "client_id": "4R0o9atlUvUvAWhNNihPSsLN",
  "message": "Machine token access"
}
```

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
