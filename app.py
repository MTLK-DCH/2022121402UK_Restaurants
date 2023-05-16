import os
from datetime import datetime, date, timedelta

import bcrypt
import jwt
from apscheduler.schedulers.background import BackgroundScheduler
from bson import ObjectId
from flask import Flask, request, jsonify, make_response, g
from flask_cors import CORS
from json import load, dump
import pymongo

# myLib
from config import app_config
from config.db_config import *
from utils.LSTM import oneday_predict, fivedays_predict
from utils.app_utils import jwt_required

os.chdir("D:\\Programing\\python\\2022121402UK_Restaurants")


def update_traffic():
    print("working")
    print(os.getcwd())
    with open("people.json") as f:
        traffic = load(f)
    print(traffic)

    today_date = date.today()
    today_datetime = datetime.now()
    strtoday = str(today_date)
    db_today = Traffic.find_one({"date": strtoday})
    if db_today is None and datetime.now().hour != 0:
        today_traffic = {
            "date": strtoday,
            "traffic": {},
            "sum": 0
        }
        for i in range(1, 25):
            today_traffic["traffic"][str(i)] = 0
        Traffic.insert_one(today_traffic)

    if db_today is None and datetime.now().hour == 0:
        yesterday = today_datetime - timedelta(days=1)
        Traffic.update_one(
            {"date": str(yesterday.date())},
            {"$set": {str(yesterday.time().hour): traffic}, "$inc": {"sum": traffic}}
        )
        with open("people.json", "w") as f:  # 再存储到文件中
            dump(0, f)
        today_traffic = {
            "date": strtoday,
            "traffic": {},
            "sum": 0
        }
        for i in range(1, 25):
            today_traffic["traffic"][str(i)] = 0
        Traffic.insert_one(today_traffic)
    else:
        Traffic.update_one(
            {"date": str(today_date)},
            {"$set": {"traffic." + str(today_datetime.time().hour): traffic}, "$inc": {"sum": traffic}}
        )
        with open("people.json", "w") as f:  # 再存储到文件中
            dump(0, f)


sched = BackgroundScheduler(daemon=True)

sched.add_job(update_traffic, 'cron', hour="*")
# sched.add_job(update_traffic, 'interval', seconds=10)
sched.start()

app = Flask(__name__)
app.config.from_object(app_config)
CORS(app, resources={r"/API/*": {"origins": "*"}})


@app.before_request
def increment_counter():
    with open("people.json") as f:  # 打开json数据 并将访问量+1
        people = load(f) + 1
        with open("people.json", "w") as f:  # 再存储到文件中
            dump(people, f)


@app.route("/")
@jwt_required
def hello_world():  # put application's code here
    return 'Hello World!'


# user functions

@app.route('/API/V1.0/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    user = Users.find_one({"username": username})
    user["_id"] = str(user["_id"])
    print(user)
    if user is not None:
        if bcrypt.checkpw(bytes(password, 'UTF-8'), user["password"]):
            token = jwt.encode(
                {
                    'user': username,
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                }, app.config['SECRET_KEY'])
            return make_response(jsonify(
                {'token': token.decode('UTF-8'), 'userid': str(user["_id"]), 'username': user["username"],
                 'email': user['email'], "role": user['role']}), 200)
        else:
            return make_response(jsonify({'message': 'Bad password'}), 401)
    else:
        return make_response(jsonify({'message': 'Bad username'}), 401)


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
            "role": 0,
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
        print(username)
        # old_password = request.json.get("old_password")
        # new_password = request.json.get("new_password")
        email = request.json.get("email")
        edited_user_data = {}
        if username is not None:
            if username == "" or Users.find_one({"username": username}) is not None:
                return make_response(jsonify({"message": "bad username"}), 409)
            else:
                edited_user_data['username'] = username
        # if old_password is not None and not bcrypt.checkpw(bytes(old_password, 'UTF-8'), user["password"]):
        #     return make_response(jsonify({"message": "bad old password"}), 412)
        # elif old_password is not None and bcrypt.checkpw(bytes(old_password, 'UTF-8'), user["password"]) and \
        #         new_password is not None:
        #     if new_password == "":
        #         return make_response(jsonify({"message": "bad new password"}), 412)
        #     else:
        #         edited_user_data["password"] = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        if email is not None and email != "":
            edited_user_data['email'] = email

        print(edited_user_data)
        Users.update_one({"_id": ObjectId(u_id)}, {"$set": edited_user_data})

        return make_response(jsonify({"message": "success"}), 200)


@app.route('/API/V1.0/user/<string:u_id>', methods=['DELETE'])
@jwt_required
def delete_user(u_id):
    if u_id is None or u_id == "" or Users.find_one({"_id": ObjectId(u_id)}) is None:
        return make_response(jsonify({"message": "Bad userid"}), 404)
    else:
        Users.delete_one({"_id": ObjectId(u_id)})
        return make_response(jsonify({"message": "success"}), 200)


@app.route('/API/V1.0/restaurant', methods=['GET'])
def load_restaurants():
    pn = 1
    ps = 6
    c = 0
    if request.args.get("pn"):
        pn = int(request.args.get("pn"))
    if request.args.get("ps"):
        ps = int(request.args.get("ps"))
    pipeline = []
    has_table_booking = request.args.get("has_table_booking")
    has_online_delivery = request.args.get("has_online_delivery")
    cuisine = request.args.get("cuisine")
    city = request.args.get("city")
    average_cost = [int(request.args.get("avg_cost0")), int(request.args.get("avg_cost1"))]
    name = request.args.get("name")
    if has_table_booking is not None and has_table_booking != "":
        pipeline.append({"$match": {"service.has_table_booking": has_table_booking}})
    if has_online_delivery is not None and has_online_delivery != "":
        pipeline.append({"$match": {"service.has_online_delivery": has_online_delivery}})
    if cuisine is not None and cuisine != "":
        pipeline.append({"$match": {"cuisines": {"$regex": cuisine}}})
    if city is not None and city != "":
        pipeline.append({"$match": {"location.city": {"$regex": city}}})
    if average_cost is not None and average_cost != "":
        pipeline.append({"$match": {"average_cost_for_two": {"$gte": average_cost[0]}}})
        pipeline.append({"$match": {"average_cost_for_two": {"$lte": average_cost[1]}}})
    if name is not None and name != "":
        pipeline.append({"$match": {"name": {"$regex": name}}})

    pipeline.append({"$project": {"name": 1, "cuisines": 1, "assessment.average_rate": 1, "assessment.votes": 1}})
    pipeline.append({"$group": {"_id": 'null', "count": {"$sum": 1}}})
    count = Restaurants.aggregate(pipeline)
    for i in count:
        c = i
    pipeline.pop()
    pipeline.append({"$skip": ps * (pn - 1)})
    pipeline.append({"$limit": ps})

    restaurants = Restaurants.aggregate(pipeline)
    result = []
    for restaurant in restaurants:
        restaurant["_id"] = str(restaurant["_id"])
        result.append(restaurant)
    return make_response(jsonify({"result": result, "count": c}), 200)
    # return make_response(result, 200)


@app.route('/API/V1.0/restaurant/<string:r_id>', methods=['GET'])
def load_one_restaurant(r_id):
    if r_id is None or r_id == "" or Restaurants.find_one({"_id": ObjectId(r_id)}) is None:
        return make_response(jsonify({"message": "Bad restaurant id"}), 404)
    else:
        restaurant_data = Restaurants.find_one({"_id": ObjectId(r_id)})
        restaurant_data['_id'] = str(restaurant_data['_id'])
        for item in restaurant_data["assessment"]["comments_list"]:
            item["_id"] = str(item["_id"])
            item["user_id"] = str(item["user_id"])
            item["user_name"] = Users.find_one({"_id": ObjectId(item["user_id"])})["username"]
        return make_response(jsonify(restaurant_data), 200)


@app.route('/API/V1.0/comment/<string:r_id>', methods=['PUT'])
@jwt_required
def add_comment(r_id):
    if r_id is None or r_id == "" or Restaurants.find_one({"_id": ObjectId(r_id)}) is None:
        return make_response(jsonify({"message": "Bad restaurant id"}), 404)
    else:
        user_id = request.json.get("user_id")
        text = request.json.get("text")
        rate = request.json.get("rate")

        if request.json.get("user_id") is None or request.json.get("user_id") == "" or \
                Users.find_one({"_id": ObjectId(request.json.get("user_id"))}) is None:
            return make_response(jsonify({"message": "Bad user id"}), 404)
        if request.json.get("text") is None or request.json.get("text") == "":
            return make_response(jsonify({"message": "Bad text"}), 412)
        if request.json.get("rate") is None or request.json.get("text") == "":
            return make_response(jsonify({"message": "Bad rate"}), 412)

        comment = {
            "_id": ObjectId(),
            "user_id": user_id,
            "text": text,
            "rate": rate,
            "time": datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }

        basic = Restaurants.find_one(
            {"_id": ObjectId("639a5f009fd2d7c465fb11b2")},
            {"_id": 0, "assessment.average_rate": 1, "assessment.votes": 1})

        average = (basic["assessment"]["average_rate"] * basic["assessment"]["votes"] + rate) / \
                  (basic["assessment"]["votes"] + 1)

        Restaurants.update_one(
            {
                "_id": ObjectId(r_id)
            }, {
                "$push":
                    {"assessment.comments_list": comment},
                '$inc':
                    {'assessment.votes': 1},
                '$set':
                    {'assessment.average_rate': average}
            })
        return make_response(jsonify({"message": "success"}), 201)

@app.route('/API/V1.0/admin', methods=['GET'])
@jwt_required
def admin():
    # 获取时间信息
    today = datetime.today().date()
    # 获取流量信息
    raw_traffics = Traffic.find().sort('_id', pymongo.DESCENDING).limit(100)
    # 打包流量信息
    today_traffic = dict(raw_traffics[0]["traffic"])
    sum_traffics = []
    sum_traffics_date = []
    for traffic in raw_traffics:
        sum_traffics.append(traffic["sum"])
        sum_traffics_date.append(traffic["date"])
    sum_traffics.reverse()
    sum_traffics_date.reverse()
    print(today_traffic)
    print("==================")
    print(sum_traffics)
    print("=================")
    print(sum_traffics_date)
    sum_30_traffics = sum_traffics[-30:]
    sum_30_traffics_date = sum_traffics_date[-30:]
    if len(sum_30_traffics) == 30:
        # 预测未来流量信息
        tomorrow = oneday_predict(sum_30_traffics)
        fivedays = fivedays_predict(sum_30_traffics)
        # 传输给前端网页
        print(tomorrow)
        print(fivedays)
        data = {
            "today": str(today),
            "today_traffic": today_traffic,
            "recent_traffic_date": sum_traffics_date,
            "recent_traffic": sum_traffics,
            "traffic_date_30": sum_30_traffics_date,
            "traffic_30": sum_30_traffics,
            "predict": fivedays
        }
        response = make_response(jsonify(data), 200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        print("error")


@app.route('/API/V1.0/test', methods=['GET'])
def test():
    data = [{"key1": request.args.get("key1")}, {"key2": request.args.get("key2")}]

    return make_response(jsonify(data), 201)


if __name__ == '__main__':
    app.run(debug=False)
