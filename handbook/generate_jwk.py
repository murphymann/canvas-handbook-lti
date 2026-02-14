import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

def int_to_base64url(num):
    """Convert an integer to base64url format."""
    num_bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
    return base64.urlsafe_b64encode(num_bytes).decode('utf-8').rstrip('=')

# Read your public key file
with open('handbook/lti_configs/public.key', 'rb') as f:
    public_key_data = f.read()

# Load the public key
public_key = load_pem_public_key(public_key_data, backend=default_backend())

# Get the public numbers
public_numbers = public_key.public_numbers()

# Convert to base64url format
n = int_to_base64url(public_numbers.n)
e = int_to_base64url(public_numbers.e)

# Create JWK
jwk = {
    "kty": "RSA",
    "alg": "RS256",
    "use": "sig",
    "e": e,
    "n": n,
    "kid": "handbook-lti-key"
}

# Print it nicely
print("\n=== Copy this entire JSON for Canvas ===\n")
print(json.dumps(jwk, indent=2))
print("\n========================================\n")