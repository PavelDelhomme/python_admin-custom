# wait_for_elasticsearch.py
import time
import requests
import os

url = os.getenv("ELASTICSEARCH_HOST", "http://admin_elasticsearch:9200")

for _ in range(10):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Elasticsearch is ready!")
            break
    except requests.ConnectionError:
        print("Waiting for Elasticsearch...")
        time.sleep(5)
else:
    print("Elasticsearch is not available after multiple attempts.")
