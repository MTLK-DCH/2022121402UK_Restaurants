import datetime

import bcrypt
import jwt
from bson import ObjectId
from flask import Flask, request, jsonify, make_response

from config import app_config
from config.db_config import *
from utils.app_utils import jwt_required

app = Flask(__name__)
app.config.from_object(app_config)


@app.route("/")
@jwt_required
def hello_world():  # put application's code here
    return 'Hello World!'


# user functions

@app.route('/API/V1.0/login', methods=['GET'])
def login():
    auth = request.authorization
    if auth:
        user = Users.find_one({"username": auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user["password"]):
                token = jwt.encode(
                    {
                        'user': auth.username,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                    }, app.config['SECRET_KEY'])
                return make_response(jsonify({'token': token.decode('UTF-8')}), 200)
            else:
                return make_response(jsonify({'message': 'Bad password'}), 401)
        else:
            return make_response(jsonify({'message': 'Bad username'}), 401)
    return make_response(jsonify({'message': 'Authentication required'}), 401)


@app.route('/API/V1.0/register', methods=['POST'])
def register():

    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")

    if username is None or username == "" or Users.find_one({"username": username}) is not None:
        return make_response(jsonify({'message': "Bad username"}), 409)
    elif password is None or password == "":
        return make_response(jsonify({"message": "Bad password"}), 412)
    elif email is None or email == "":
        return make_response(jsonify({"message": "Bad email"}), 412)
    else:
        user = {
            "username": request.json.get("username"),
            "password": request.json.get("password"),
            "email": request.json.get("email"),
            "subscribe": [
            ]
        }
        user['password'] = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt())
        Users.insert_one(user)
        return make_response(jsonify({"message": "success"}), 201)


@app.route('/API/V1.0/subscribe/<string:u_id>', methods=['GET'])
@jwt_required
def get_subscribe(u_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    else:
        subscribe_dict = Users.find_one({"_id": ObjectId(u_id)}, {"_id": 0, "subscribe": 1})
        subscribe_list = subscribe_dict["subscribe"]
        return make_response(jsonify(subscribe_list), 200)


@app.route('/API/V1.0/subscribe/<string:u_id>/<string:r_id>', methods=['PUT'])
@jwt_required
def add_subscribe(u_id, r_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    elif r_id is None or r_id == "" or Restaurants.find_one({"_id": ObjectId(r_id)}) is None:
        return make_response(jsonify({"message": "Bad restaurant id"}), 404)
    else:
        name = Restaurants.find_one({"_id": ObjectId(r_id)}, {"_id": 0, "name": 1})
        subscribe = {
            "restaurant_id": r_id,
            "restaurant_name": name['name']
        }
        Users.update_one({"_id": ObjectId(u_id)}, {"$push": {"subscribe": subscribe}})
        return make_response(jsonify({"message": "success"}), 201)


@app.route('/API/V1.0/subscribe/<string:u_id>/<string:r_id>', methods=['DELETE'])
@jwt_required
def delete_subscribe(u_id, r_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    elif r_id is None or r_id == "" or Restaurants.find_one({"_id": ObjectId(r_id)}) is None:
        return make_response(jsonify({"message": "Bad restaurant id"}), 404)
    else:
        Users.update_one({"_id": ObjectId(u_id)}, {"$pull": {"subscribe": {"restaurant_id": r_id}}})
        return make_response(jsonify({"message": "success"}), 200)


@app.route('/API/V1.0/user/<string:u_id>', methods=['GET'])
@jwt_required
def load_user_details(u_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    else:
        user_data = Users.find_one({"_id": ObjectId(u_id)}, {"_id": 0, "password": 0, "subscribe": 0})
        return make_response(jsonify(user_data), 200)


@app.route('/API/V1.0/user/<string:u_id>', methods=['PUT'])
@jwt_required
def edit_user_details(u_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    else:
        user = Users.find_one({"_id": ObjectId(u_id)})
        username = request.json.get("username")
        old_password = request.json.get("old_password")
        new_password = request.json.get("new_password")
        email = request.json.get("email")
        edited_user_data = {}
        if username is not None:
            if username == "" or Users.find_one({"username": username}) is not None:
                return make_response(jsonify({"message": "bad username"}), 409)
            else:
                edited_user_data['username'] = username
        if old_password is not None and not bcrypt.checkpw(bytes(old_password, 'UTF-8'), user["password"]):
            return make_response(jsonify({"message": "bad old password"}), 412)
        elif old_password is not None and bcrypt.checkpw(bytes(old_password, 'UTF-8'), user["password"]) and \
                new_password is not None:
            if new_password == "":
                return make_response(jsonify({"message": "bad new password"}), 412)
            else:
                edited_user_data["password"] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        if email is not None and email != "":
            edited_user_data['email'] = email

        Users.update_one({"_id": ObjectId(u_id)}, {"$set": edited_user_data})

        return make_response(jsonify({"message": "success"}), 200)


if __name__ == '__main__':
    app.run(debug=True)
