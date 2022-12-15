from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017")
# select database
db = client.UK_Restaurant
# select collection
Users = db.Users
Restaurants = db.Restaurants
Raw = db.originaldata


