import pyotp

# Use the mfa_secret as the TOTP secret
secret = "GBYHMZDVMVRVIV3YJ44G66LNPFRXG6LC"

# Generate the TOTP
totp = pyotp.TOTP(secret)
print("Generated TOTP:", totp.now())  # This will print the OTP