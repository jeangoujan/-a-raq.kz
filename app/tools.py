import jwt 

def create_jwt(user_id: int) -> str:
    body = {"user_id": user_id}
    token = jwt.encode(body, "jeangoujan", algorithm="HS256")
    return token

def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "jeangoujan", algorithms=["HS256"])
    return data["user_id"]
