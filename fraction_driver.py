import asyncio
import json
import logging
from redis import Redis
from typing import Dict
from utils.fraction_collector_com import get_redis_bool

logging.basicConfig(level=logging.INFO)


async def discrete_collect(
    r: Redis,
    load_volume_to_collect: float,
    stop_collect: bool = False,
):
    load_duration = float(r.get(f"load_duration"))
    load_flowrate = float(r.get(f"load_flow_rate"))
    load_status: Dict[str:float, str:str] = json.loads(r.get(f"load_status"))

    current_step = load_status["step"]
    percent_complete = float(load_status["percent_done"])

    loaded_volume = load_duration * (1 - percent_complete) * load_flowrate

    if (
        current_step == "load"
        and loaded_volume > load_volume_to_collect
        and not (stop_collect)
        and not (get_redis_bool(r, f"discrete-fractionate", False))
    ):
        load_volume_to_collect += 20
        r.set(f"discrete-fractionate", f"{True}")
        # stop_collect = True

    if current_step != "load":
        load_volume_to_collect = 60
        stop_collect = False

    logging.info(
        f"load_volume_to_collect: {load_volume_to_collect}\tloaded_volume: {loaded_volume:.2f}"
    )

    if load_volume_to_collect >= 180:
        stop_collect = True
        raise SystemExit()

    return load_volume_to_collect


async def continuous_collect(r: Redis, stop_collect: bool = False):
    load_duration = float(r.get(f"load_duration"))
    load_flowrate = float(r.get(f"load_flow_rate"))
    load_status: Dict[str:float, str:str] = json.loads(r.get(f"load_status"))

    current_step = load_status["step"]
    percent_complete = float(load_status["percent_done"])
    load_volume_to_collect = 60

    loaded_volume = load_duration * (1 - percent_complete) * load_flowrate

    if current_step in ["wash", "load", "elute"]:
        if current_step == "elute":
            r.set(f"outlet_to_divert", 10)
        else:
            r.set(f"outlet_to_divert", 12)
        r.set(f"fc_outlet", 14)
        r.set(f"continuous-fractionate", f"{True}")

    if get_redis_bool(r, f"continuous-fractionate", False) is False:
        raise SystemExit()


async def main():
    redis_client = Redis("10.20.18.65", decode_responses=True)
    load_volume_to_collect = 40
    try:
        while True:
            # await continuous_collect(redis_client)
            load_volume_to_collect = await discrete_collect(
                redis_client, load_volume_to_collect
            )

            await asyncio.sleep(0.5)
    except SystemExit:
        pass


if __name__ == "__main__":
    # redis_client = Redis("10.20.18.65", decode_responses=True)

    # load_status: Dict[str:float, str:str] = json.loads(redis_client.get(f"load_status"))

    # current_step = load_status["step"]

    # asyncio.run(continuous_collect(redis_client))
    asyncio.run(main())
