import os
import string
import logging
import json
import time
import asyncio
from collectionlogic.collector import CollectionLogic
from recipes.continuous_collection import checkrun_continuous
from recipes.discrete_collection import checkrun_discrete
from utils.fraction_collector_com import set_diverter_valve
from redis import Redis
from pymongo import MongoClient

REDIS_URL = os.environ.get("REDIS_URL", "10.20.18.65")
MONGO_URL = os.environ.get(
    "MONGO_URL", "mongodb:dsp_database_user:biosmb@10.20.18.65:27017"
)

logging.basicConfig(level=logging.DEBUG)


async def main():
    redis_client = Redis(REDIS_URL, decode_responses=True)

    continuous_task = asyncio.create_task(
        checkrun_continuous(redis_client, "continuous-fractionation")
    )
    discrete_task = asyncio.create_task(
        checkrun_discrete(redis_client, "discrete-fractionation")
    )

    await continuous_task
    await discrete_task


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except Exception as ex:
        logging.debug(f"[MAIN] Error encountered: {ex}")
    except KeyboardInterrupt:
        pass
    finally:
        set_diverter_valve(False)
