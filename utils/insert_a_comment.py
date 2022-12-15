from bson import ObjectId

from config.db_config import *

comment = {
    "_id": ObjectId(),
    "user_id": ObjectId("639a547b1831a885705de0af"),
    "text": "I like it",
    "rate": 5
}

Restaurants.update_one(
    {
        "_id": ObjectId("639a5f009fd2d7c465fb11b2")
    },
    {
        "$push": {
            "assessment.comments_list": comment
        }
    }
)
