import pyotp
import base64

# Base32 encoding of 'admin'
username = 'admin'
base32_secret = base64.b32encode(username.encode()).decode()

print("Base32 Encoded 'admin':", base32_secret)

# Generate the TOTP
totp = pyotp.TOTP(base32_secret)
print("Generated TOTP:", totp.now())  # This will give you the one-time password (OTP)