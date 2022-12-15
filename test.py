from bson import ObjectId

from config.db_config import Users, Restaurants

result = Restaurants.find_one({"_id": ObjectId("639a5f009fd2d7c465fb11b2")}, {"_id": 0, "name": 1})
print(result)
