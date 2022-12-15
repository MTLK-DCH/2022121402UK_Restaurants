import bcrypt

from config.db_config import *

user = {
    "username": "user01",
    "password": "12345",
    "email": "a@b.c",
    "subscribe": [
        {
            "restaurant_id": "",
            "restaurant_name": ""
        }
    ]
}

user['password'] = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt())

# Users.insert_one(user)
print(user)