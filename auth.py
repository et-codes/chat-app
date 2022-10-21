import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')


def create_token(username):
    expiration_date = datetime.today() + timedelta(hours=24)
    payload_data = {
        "username": username,
        "expiration": expiration_date.isoformat()
    }
    token = jwt.encode(
        payload=payload_data,
        key=SECRET_KEY,
        algorithm='HS256'
    )
    return token


def check_token(token):
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms='HS256'
        )
        return payload
    except:
        return False


if __name__ == '__main__':
    username = 'eric'
    token = create_token(username)
    print(token)
    token_data = check_token(token)
    print(token_data)
