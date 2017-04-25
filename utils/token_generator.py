
import uuid

def generate_token():
    token = uuid.uuid4().hex
    return token

