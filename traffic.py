import time

def worker(shared_data):
    while True:
        # 每小时获取一次主进程的数据
        time.sleep(5)
        data = shared_data.value
        print(f"Got data from main process: {data}")