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

# today = datetime.date.today()
# print(today)
# print(type(today))
# str_date = str(today)
# print(type(str_date))

# today = date.today()
# today = str(today)
# db_today = Traffic.find_one({"date": today})
# if db_today is None:
#     today_traffic = {
#         "date": today,
#         "traffic": {},
#         "sum": 0
#     }
#     for i in range(1, 25):
#         today_traffic["traffic"][str(i)] = 0
#
# print(today_traffic)

# print(os.getcwd())
# with open("people.json") as f:  # 打开json数据 并将访问量+1
#     people = load(f) + 1
#     with open("people.json", "w") as f:  # 再存储到文件中
#         dump(people, f)
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
sum_30_traffics_date = sum_traffics_date[-30]
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
        "30_traffic_date": sum_30_traffics_date,
        "30_traffic": sum_30_traffics,
        "predict": fivedays
    }

