import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

from fractioncollector.fractionator import FractionCollector
from collectionlogic.collector import CollectionLogic
from redis import Redis

REDIS_URL = os.environ.get("REDIS_URL", "localhost")


async def main():
    redis_client = Redis(REDIS_URL, decode_responses=True)
    cl = CollectionLogic(redis_client)
    x = await cl.discrete_fractionate()

    print(x)


if __name__ == "__main__":
    fc = FractionCollector()
    info = fc.get_actual_plate_info(0)
    asyncio.run(main())
    print(fc)

    
