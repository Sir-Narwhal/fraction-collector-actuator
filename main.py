import os
import string
import logging
import json
import time
from collectionlogic.collector import CollectionLogic
from redis import Redis
from pymongo import MongoClient

REDIS_URL = os.environ.get("REDIS_URL", "10.20.18.65")
MONGO_URL = os.environ.get(
    "MONGO_URL", "mongodb:dsp_database_user:biosmb@10.20.18.65:27017"
)


def main():

    redis_client = Redis(REDIS_URL, decode_responses=True)
    fc_logic = CollectionLogic()

    fraction_conditions = {
        "load": [
            0.25,
            0.40,
            0.50,
            0.60,
            0.75,
        ],
        "elute": [0.1],
        "wash": [0.1],
        "load bypass": [0.1],
    }

    tol = 0.5

    try:
        while True:
            load_status = json.loads(redis_client.get("load_status"))
            latest_obs = json.loads(redis_client.get("latest_observation"))

            percent_done = load_status["percent_done"]
            step = load_status["step"]

            # else:
            #     continue

            time.sleep(2)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":

    main()
