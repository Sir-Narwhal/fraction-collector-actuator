import os
import asyncio
import logging
from redis import Redis
from collectionlogic.collector import CollectionLogic
from utils.fraction_collector_com import set_diverter_valve, get_redis_bool

"""
Tasks: 
()      Do so when redis value says to continuous collect
(i)     Advance the fraction collector when desired volume has been collected in the well. 
(ii)    Store {time, total volume collected, well location} in MongoDB

"""

REDIS_URL = os.environ.get(f"REDIS_URL", "10.20.18.65")


async def checkrun_continuous(r: Redis, expr_name: str):

    try:
        collector = CollectionLogic(r, expr_name, fc_samplevolume=1.0)

        while True:
            if get_redis_bool(r, "continuous-fractionate", False) and not (
                get_redis_bool(r, "discrete-fractionate", False)
            ):
                await collector.continuous_fractionate()
                logging.debug(f"[FC Continuous] Continous Fractionation Over.")

            await asyncio.sleep(0.5)
    except Exception as ex:
        logging.debug(f"[FC Continous] Exception occurred: {ex}")
    finally:
        set_diverter_valve(False)
        logging.debug(f"[FC Continuous] Diverter Valve Turned Off")


if __name__ == "__main__":
    redis_client = Redis(REDIS_URL, decode_responses=True)
    asyncio.run(checkrun_continuous(redis_client, "test-continuous-fractionation"))
