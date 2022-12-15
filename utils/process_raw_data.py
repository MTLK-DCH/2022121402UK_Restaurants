from config.db_config import *

data = []

for restaurant in Raw.find():
    if 'code' in restaurant:
        continue
    a = restaurant['restaurants']
    for restaurants in a:
        item = restaurants["restaurant"]
        if item["location"]['country_id'] == 215:
            after = {
                "name": item['name'],
                "cuisines": item['cuisines'].split(', '),
                "location": {
                    "address": item["location"]["address"],
                    "city": item["location"]["city"],
                    "zipcode": item["location"]["zipcode"]
                },
                "url": item["url"],
                "menu": item["menu_url"],
                "average_cost_for_two": item["average_cost_for_two"],
                "service": {
                    "has_table_booking": item["has_table_booking"],
                    "has_online_delivery": item["has_online_delivery"]
                },
                "assessment": {
                    "average_rate": 0,
                    "votes": 0,
                    "comments_list": [
                    ]
                }
            }
            data.append(after)

Restaurants.insert_many(data)
