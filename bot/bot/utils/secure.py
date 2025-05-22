import hmac
import hashlib
import base64


def generate_secure_token(secure_key, user_id):
    print(f"User_id: {user_id}, key: {secure_key}")
    message = str(user_id).encode()
    secret = str(secure_key).encode()
    token = hmac.new(secret, message, hashlib.sha256).digest()

    return base64.urlsafe_b64encode(token).decode()
