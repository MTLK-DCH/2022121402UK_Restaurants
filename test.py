from bson import ObjectId

from config.db_config import Restaurants
from bson import ObjectId

from config.db_config import Restaurants
#
# r_id = ObjectId("639a5f009fd2d7c465fb11b2")
# # time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
# #
# # comment = {
# #     "_id": ObjectId(),
# #             "user_id": ObjectId("639a6517b7fe5a5e5828d0e0"),
# #             "text": "text",
# #             "rate": 2,
# #             "time": time
# #         }
# #
# # basic = Restaurants.find_one(
# #             {"_id": ObjectId("639a5f009fd2d7c465fb11b2")},
# #             {"_id": 0, "assessment.average_rate": 1, "assessment.votes": 1})
# #
# # average = (basic["assessment"]["average_rate"] * basic["assessment"]["votes"] + comment["rate"]) / \
# #           (basic["assessment"]["votes"] + 1)
#
# # Restaurants.update_one({"_id": ObjectId("639a5f009fd2d7c465fb11b2")}, {"$push": {"assessment.comments_list": comment}})
#
# # result = Restaurants.find_one({"_id": ObjectId("639a5f009fd2d7c465fb11b2")}, {"_id": 0, "assessment.average_rate": 1})["assessment"]["average_rate"]
# # Restaurants.update_one(
# #             {
# #                 "_id": ObjectId("639a5f009fd2d7c465fb11b2")
# #             }, {
# #                 "$push":
# #                     {"assessment.comments_list": comment},
# #                 '$inc':
# #                     {'assessment.votes': 1},
# #                 '$set':
# #                     {'assessment.average_rate': average}
# #             })
# # result = Restaurants.find_one({"_id": ObjectId("639a5f009fd2d7c465fb11b2")})
# # restaurant_data = Restaurants.find_one({"_id": ObjectId(r_id)})
# # restaurant_data['_id'] = str(restaurant_data['_id'])
# # for item in restaurant_data["assessment"]["comments_list"]:
# #     item["_id"] = str(item["_id"])
# #     item["user_id"] = str(item["user_id"])
# #     item["user_name"] = Users.find_one({"_id": ObjectId(item["user_id"])})["username"]
#
pipeline = [
    # service
    {"$match": {"service.has_table_booking": 0}},
    {"$match": {"service.has_online_delivery": 0}},
    # cuisine
    {"$match": {"cuisines": {"$regex": "Indian"}}},
    # city
    {"$match": {"location.city": {"$regex": "London"}}},
    # average_cost
    {"$match": {"average_cost_for_two": {"$gte": 30}}},
    {"$match": {"average_cost_for_two": {"$lte": 40}}},
    # name
    {"$match": {"name": {"$regex": ""}}},
    {"$project": {"name": 1, "cuisines": 1, "assessment.average_rate": 1, "assessment.votes": 1}},

]
#
# pipeline = [
#     {'$match': {'average_cost_for_two': {'$gte': '0'}}},
#     {'$match': {'average_cost_for_two': {'$lte': '1000'}}},
#     {'$project': {'name': 1, 'cuisines': 1, 'assessment.average_rate': 1, 'assessment.votes': 1}},
#     # {'$group': {'_id': 'null', 'count': {'$sum': 1}}}
# ]
#
#
# results = Restaurants.aggregate(pipeline)
#
# for result in results:
#     print(result)
from config.db_config import Users

Users.update_one({"_id": ObjectId('639a547b1831a885705de0af')}, {"$set": {"username": "newuser"}})
