import asyncio
from fractioncollector.fractionator import FractionCollector
from collectionlogic.collector import CollectionLogic
from redis import Redis


async def main():
    redis_client = Redis("10.20.18.65", decode_responses=True)
    cl = CollectionLogic(redis_client)
    x = await cl.discrete_fractionate()

    print(x)


if __name__ == "__main__":
    fc = FractionCollector()
    info = fc.get_actual_plate_info(0)
    asyncio.run(main())
    print(fc)

    
