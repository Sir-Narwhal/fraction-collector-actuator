import os
import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from redis import Redis
from utils.fraction_collector_com import (
    set_diverter_valve,
    get_redis_bool,
    set_redis_bool,
)
from collectionlogic.collector import CollectionLogic

REDIS_URL = os.environ.get("REDIS_URL", "localhost")


async def checkrun_discrete(r: Redis, expr_name):

    try:
        collector = CollectionLogic(r, expr_name, fc_samplevolume=0.50)
        while True:

            logging.debug(
                f"discrete-fractionate: {get_redis_bool(r, 'discrete-fractionate', False)}\tcontinuous-fractionate: {get_redis_bool(r, 'continuous-fractionate', False)}"
            )
            if get_redis_bool(r, "discrete-fractionate", False) and not (
                get_redis_bool(r, "continuous-fractionate", False)
            ):
                await collector.discrete_fractionate()
                set_redis_bool(r, "discrete-fractionate", False)
                logging.debug(
                    f"[FC Discrete] Setting key (discrete-fractionate) to FALSE"
                )
                logging.debug(f"[FC Discrete] Discrete Fractionation Over.")
            else:
                await asyncio.sleep(0.5)
    except Exception as ex:
        logging.debug(f"[FC Discrete] Exception occurred: {ex}")
    finally:
        set_diverter_valve(False)
        set_redis_bool(r, "discrete-fractionate", False)
        logging.debug(f"[FC Discrete] Diverter Valve Turned Off")


if __name__ == "__main__":
    redis_client = Redis(REDIS_URL, decode_responses=True)
    asyncio.run(checkrun_discrete(redis_client, "test-continuous-fractionation"))

    # fraction_conditions = {
    #     "load": [
    #         0.25,
    #         0.40,
    #         0.50,
    #         0.60,
    #         0.75,
    #     ],
    #     "elute": [0.1],
    #     "wash": [0.1],
    #     "load bypass": [0.1],
    # }
