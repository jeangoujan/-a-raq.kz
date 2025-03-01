import jwt

def create_jwt(user_id: int) -> int:
    body = {"user_id": user_id}
    token = jwt.encode(body, "jeangoujan", "HS256")
    return token

def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "jeangoujan", "HS256")
    return data["user_id"]