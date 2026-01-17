import logging
from redis import Redis
from pymodbus.client import ModbusTcpClient


def advance_fc():
    try:
        client = ModbusTcpClient("10.20.20.25")
        client.connect()
        client.write_coil(16384, True)

    except Exception as e:
        logging.warning("Failed to advance fraction collector")
        logging.warning(e)
    finally:
        client.close()


def set_diverter_valve(divert: bool):
    try:
        client = ModbusTcpClient("10.20.20.25")
        client.connect()
        client.write_coil(8265, divert)

    except Exception as e:
        logging.warning("Failed to set fraction collector diverter")
        logging.warning(e)
    finally:
        client.close()


def set_redis_bool(r: Redis, key: str, value: bool):
    try:
        r.set(key, f"{value}")
    except Exception as ex:
        logging.warning(f"[Redis]: Unable to set key ({key}) with value ({value})")
        logging.error(f"Error Encountered: {ex}")


def get_redis_bool(r: Redis, key: str, default_value: bool):
    truth_list = ["true", "1", "yes", "y", "on"]
    try:
        return r.get(key).lower() in truth_list
    except Exception as ex:
        logging.warning(f"[Redis]: Unable to get key ({key})")
        logging.error(f"Error Encountered: {ex}")
        return default_value


def set_redis_int(r: Redis, key: str, value: int):
    try:
        r.set(key, f"{value}")
    except Exception as ex:
        logging.warning(f"[Redis]: Unable to set key ({key}) with value ({value})")
        logging.error(f"Error Encountered: {ex}")


def get_redis_int(r: Redis, key: str, default_value: int):
    try:
        return int(r.get(key))
    except Exception as ex:
        logging.warning(f"[Redis]: Unable to get key ({key})")
        logging.error(f"Error Encountered: {ex}")
        return default_value


if __name__ == "__main__":
    set_diverter_valve(False)
