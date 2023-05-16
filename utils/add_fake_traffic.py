import random
from datetime import date, datetime, timedelta

from config.db_config import Traffic

today = datetime.today()
today_date = today.date()
for _ in range(1, 101):
    date = today - timedelta(days=100 - _)
    today_traffic = {
        "date": str(date.date()),
        "traffic": {},
        "sum": 0
    }
    for i in range(1, 25):
        today_traffic["traffic"][str(i)] = random.randint(1, 100)
        today_traffic["sum"] += today_traffic["traffic"][str(i)]
    Traffic.insert_one(today_traffic)