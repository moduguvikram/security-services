
# Security Services - OAuth2 Server with OTP

## Prerequisites

- Python 3.9+
- Poetry Package Manager

## Dependencies

- flask
- flask-sqlalchemy
- authlib
- werkzeug
- pyotp
- qrcode
- pillow
- mangum

## Installation

```bash
poetry install
```

## Run the Server

```bash
python3 api/app.py
``` 


1️⃣ Register a user

curl -X POST https://127.0.0.1:5000/register_user -H "Content-Type: application/json" -d '{"username":"modugu","password":"vikram123"}' -k

{
  "message": "User registered",
  "otp_uri": "otpauth://totp/ThisOAuthServer:modugu?secret=M5LN4KVVZE2NYLXGW2U34KSE7Z6SUGB2&issuer=ThisOAuthServer"
}
Response gives you an otp_uri.
Scan it in Google Authenticator.


Verify OTP:

curl -X POST https://127.0.0.1:5000/verify_otp \
  -H "Content-Type: application/json" \
  -d '{"username":"modugu","code":"056628"}' -k

  Response:

curl -X POST https://127.0.0.1:5000/verify_otp \
  -H "Content-Type: application/json" \
  -d '{"username":"modugu","code":"091204"}' -k
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

curl -X POST https://127.0.0.1:5000/token  -u "4R0o9atlUvUvAWhNNihPSsLN:J3oq2uHDGdJQbz7zlwjOSnECYqplEXj34eH3SCOzK0liV4kO" -d "grant_type=password&username=modugu&password=vikram123" -k


{"access_token": "MTV3IBXhMhrs6RnKAx6jJ0wgXZN1ooq5pbXHI7F2YE", "expires_in": 864000, "refresh_token": "g67yHraHSKeShhelY8VVjfcjEDwx9iAbAcBbdno1nDvsV5KU", "token_type": "Bearer"}%                  


client credentials verification

curl -X POST https://127.0.0.1:5000/create_client -H "Content-Type: application/json" -d '{"client_name":"ServiceApp","redirect_uri":"https://localhost/callback"}' -k
{
  "client_id": "fZ4AqsZFTgMNvfIzaCPutJuB",
  "client_secret": "F7N6SSm2ipEQOrfwEThDfbzW1R0kia5qy55ZR77ofsvJnEaC"
}

Save the returned client_id and client_secret.

curl -X POST https://127.0.0.1:5000/token -u "jxBm4BIM4WFIHi0ZsiUlG5W4:eMtqnmtNQVlw5RA4N3GGqQSPrfdcEfH2oGTT9ppQ1MWj25q9"  -d "grant_type=client_credentials&scope=profile" -k

{"access_token": "GPSlmILLMF3W1GMNyVqJN4GSnwmuiKr02zbT4iaZ1f", "expires_in": 864000, "scope": "profile", "token_type": "Bearer"}%

curl https://127.0.0.1:5000/profile  -H "Authorization: Bearer N2KproeimHJ3J4Kum2OBVVZhWZqqf62O8dsPtjtITh" -k