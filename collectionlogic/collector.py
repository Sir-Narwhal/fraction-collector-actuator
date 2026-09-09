import os
import json
import logging
import asyncio
from redis import Redis
from pymongo import MongoClient
from typing import Dict, Tuple
from datetime import datetime, timezone
from fractioncollector import FractionCollector
from utils import (
    advance_fc,
    set_diverter_valve,
    set_redis_bool,
    get_redis_int,
    get_redis_bool,
)
from collectionlogic.deadvolume import (
    get_divertervalve_collection_dv,
    get_biosmb_to_divertervalve_dv,
)
from collectionlogic.exceptions import CollectorLogicError, NoFlowrateError

MONGO_URL = os.environ.get("MONGO_URL")

FC_OUTLET = "fc_outlet"
FC_DEFAULT = "outlet_to_divert"
FC_COMMAND = "fractionate"
FC_DEADVOLUME = ""

"""
    Steps: 
        -> set biosmb valve to fraction collector (fractionate)
        |    |
        |    |-> (1) wait until dead volume between biosmb and 
        |    |          diverter valve is evacuated
        |    |-> (2) switch on diverter valve
        |    |
        |    |-> (3) wait until dead volume between diverter 
        |    |          valve and fractions is evacuated (1.4 mL)
        |    |-> (4) advance_fc() and increment global idx by one
        |    |
        |    |-> (5) wait until sample is collected (1.6 mL) 
        |    |
        |    |-> (6) switch off divert valve 
        |    |
        |    |-> (7) set biosmb valve from fraction collector to waste

    Inputs (from Redis): 
        |
        |   -     fractionate => swap valve from fc to waste or vice versa
        | 
        |   -     dead_volume => bewteen biosmb and diverter valve
        |
        |   -     flowrate => going to fraction collector
    
    Outputs (to Redis): 
        |   
        |   -     fractionation well info : Dict 
        |
        |   -     global index : int
        |
"""


class CollectionLogic:
    """To be able to clearly define what happens when called to collect, this class nicely
    organizes everything in one place so that the actuator logic can decide when to run
    samples and when not to.
    """

    def __init__(
        self,
        redis_client: Redis,
        expr_name: str = "default_experiment",
        fc_samplevolume: float = 1.6,
        mongo_client_url: str = None,
        mongo_db_name: str = "dsp_db",
        mongo_collection_name: str = "fraction-collector-data",
    ):
        self.fc = FractionCollector()
        self.redis_client = redis_client
        self.mongo_client_url = mongo_client_url or MONGO_URL
        self.expr_name = expr_name
        self.fc_samplevolume = fc_samplevolume  # [=] mL

        # redis keys
        self.global_index_key = "fractioncollector_index"
        self.flowrate_key = "latest_observation"
        self.fractionate_key = "fractionate"

        # redis values
        self.flowrate = self.get_flowrate()  # [=] mL/min
        self._global_index = 1

        # well metadata
        self.wellplate_info = self.get_wellplate_info(self._global_index)

        # mognodb collection and db
        self.mongo_db_name = mongo_db_name
        self.mongo_collection_name = mongo_collection_name

    @property
    def global_index(self):
        self._global_index = get_redis_int(self.redis_client, self.global_index_key, 1)
        return self._global_index

    @global_index.setter
    def global_index(self, idx: int):
        try:
            self.redis_client.set(self.global_index_key, idx)
        except Exception as ex:
            logging.warning(
                f"Unable to write {self.global_index.__name__} as {self.global_index_key}:{idx}"
            )
            logging.error(f"Error: {ex}")
        self._global_index = idx
        return self._global_index

    def get_flowrate(self):
        latest_obs = json.loads(self.redis_client.get(self.flowrate_key))
        if latest_obs is None:
            logging.fatal(f"Unable to get redis value for key: {self.flowrate_key}!")
            raise NoFlowrateError(f"Expected flowrate value from redis. Got None")

        key = "biosmb_flows"

        if key not in latest_obs.keys():
            logging.fatal(
                f"Unable to get '{key}' value from redis key: {self.flowrate_key}!"
            )
            raise NoFlowrateError(f"Expected flowrate value from redis. Got None")

        flowrates = latest_obs[key]
        return max(flowrates)

    def get_wellplate_info(self, idx: int) -> Dict:
        return self.fc.get_actual_plate_info(idx)

    async def discrete_fractionate(self) -> Tuple[Dict[str, object], Dict[str, object]]:
        cycle_id = json.loads(self.redis_client.get("latest_observation"))["cycle_tag"]
        # Step 0:
        set_redis_bool(self.redis_client, key=self.fractionate_key, value=True)
        self.flowrate = self.get_flowrate()  # [=] mL/min

        # Step 1:
        dv_biosmb_to_diverter = get_biosmb_to_divertervalve_dv()  # [=] mL
        deadtime_biosmb_to_diverter = dv_biosmb_to_diverter / self.flowrate  # [=] min

        await asyncio.sleep(deadtime_biosmb_to_diverter * 60)
        dv_info_1 = self.get_wellplate_info(self.global_index)

        # Step 2:
        set_diverter_valve(True)
        dv_info_1["start_time"] = datetime.now(timezone.utc)

        # Step 3: TODO Separate into two fractions (DEAD VOLUME)
        dv_diverter_to_collection = get_divertervalve_collection_dv()  # [=] mL
        deadtime_diverter_to_collection = (
            dv_diverter_to_collection / self.flowrate
        )  # [=] min
        await asyncio.sleep(deadtime_diverter_to_collection * 60 / 2)
        dv_info_1["end_time"] = datetime.now(timezone.utc)
        dv_info_1["expr_name"] = "DEAD VOLUME #1"
        dv_info_1["cycle_tag"] = cycle_id

        self.global_index += 1
        dv_info_2 = self.get_wellplate_info(self.global_index)
        advance_fc()

        dv_info_2["start_time"] = datetime.now(timezone.utc)
        await asyncio.sleep(deadtime_diverter_to_collection * 60 / 2)
        dv_info_2["end_time"] = datetime.now(timezone.utc)
        dv_info_2["expr_name"] = "DEAD VOLUME #2"
        dv_info_2["cycle_tag"] = cycle_id

        # Step 4:
        self.global_index += 1
        sample_info = self.get_wellplate_info(self._global_index)
        advance_fc()
        sample_info["start_time"] = datetime.now(timezone.utc)

        # Step 5:
        self.flowrate = self.get_flowrate()  # [=] mL/min
        deadtime_sample_collection = self.fc_samplevolume / self.flowrate  # [=] min

        await asyncio.sleep(deadtime_sample_collection * 60)
        sample_info["end_time"] = datetime.now(timezone.utc)
        sample_info["expr_name"] = self.expr_name

        # Step 6:
        set_diverter_valve(False)

        # Step 7:
        set_redis_bool(self.redis_client, key=self.fractionate_key, value=False)

        # Step 8:
        self.global_index += 1
        advance_fc()

        # Step 9: Load to MongoDB
        step_info = json.loads(self.redis_client.get(f"load_status"))
        sample_info["step"] = step_info["step"]

        cycle_id = json.loads(self.redis_client.get("latest_observation"))["cycle_tag"]
        sample_info["cycle_tag"] = cycle_id

        try:
            with MongoClient(f"{self.mongo_client_url}") as mongo_client:
                mongo_db = mongo_client.get_database(f"{self.mongo_db_name}")
                mongo_coll = mongo_db.get_collection(f"{self.mongo_collection_name}")
                mongo_coll.insert_one(dv_info_1)
                mongo_coll.insert_one(dv_info_2)
                mongo_coll.insert_one(sample_info)

            logging.debug(f"[MongoDB] Successful entry to MongoDB")

        except Exception as ex:
            logging.error(f"[MongoDB] Error occurred: {ex}")

        return dv_info_1, sample_info

    async def continuous_fractionate(self) -> Dict[str, object]:
        cycle_id = json.loads(self.redis_client.get("latest_observation"))["cycle_tag"]

        # Step 0:
        set_redis_bool(self.redis_client, key=self.fractionate_key, value=True)
        logging.debug(f"[REDIS] Set key ({self.fractionate_key}) to TRUE")

        self.flowrate = self.get_flowrate()  # [=] mL/min
        # Step 1:
        dv_biosmb_to_diverter = get_biosmb_to_divertervalve_dv()  # [=] mL
        deadtime_biosmb_to_diverter = dv_biosmb_to_diverter / self.flowrate  # [=] min
        await asyncio.sleep(deadtime_biosmb_to_diverter * 60)
        dv_info_1 = self.get_wellplate_info(self.global_index)
        logging.debug(f"[FC] Collected wellplate data: {dv_info_1}")

        # Step 2:
        set_diverter_valve(True)
        dv_info_1["start_time"] = datetime.now(timezone.utc)
        logging.debug(f"[FC] Diverter Valve turned off")

        # Step 3: Purge diverter valve
        dv_diverter_to_collection = get_divertervalve_collection_dv()  # [=] mL
        deadtime_diverter_to_collection = (
            dv_diverter_to_collection / self.flowrate
        )  # [=] min

        await asyncio.sleep(deadtime_diverter_to_collection * 60 / 2)
        dv_info_1["end_time"] = datetime.now(timezone.utc)
        dv_info_1["expr_name"] = "DEAD VOLUME #1"
        dv_info_1["cycle_tag"] = cycle_id

        self.global_index += 1
        dv_info_2 = self.get_wellplate_info(self.global_index)
        advance_fc()

        dv_info_2["start_time"] = datetime.now(timezone.utc)
        await asyncio.sleep(deadtime_diverter_to_collection * 60 / 2)
        dv_info_2["end_time"] = datetime.now(timezone.utc)
        dv_info_2["expr_name"] = "DEAD VOLUME #2"
        dv_info_2["cycle_tag"] = cycle_id

        try:
            with MongoClient(f"{self.mongo_client_url}") as mongo_client:
                mongo_db = mongo_client.get_database(f"{self.mongo_db_name}")
                mongo_coll = mongo_db.get_collection(f"{self.mongo_collection_name}")
                mongo_coll.insert_one(dv_info_1)
                mongo_coll.insert_one(dv_info_2)

            logging.debug(f"[MongoDB] Successful entry to MongoDB")

        except Exception as ex:
            logging.error(f"[MongoDB] Error occurred: {ex}")

        continuous_fractionation_bool = self.redis_client.get("continuous-fractionate")
        while continuous_fractionation_bool:
            # Step 4:
            self.global_index += 1
            logging.debug(f"[FC] Collecting fraction # {self.global_index}")
            sample_info = self.get_wellplate_info(self._global_index)
            advance_fc()
            sample_info["start_time"] = datetime.now(timezone.utc)

            self.flowrate = self.get_flowrate()  # [=] mL/min
            # Step 5:
            deadtime_sample_collection = self.fc_samplevolume / self.flowrate  # [=] min
            await asyncio.sleep(deadtime_sample_collection * 60)
            sample_info["end_time"] = datetime.now(timezone.utc)
            sample_info["expr_name"] = self.expr_name

            step_info = json.loads(self.redis_client.get(f"load_status"))
            sample_info["step"] = step_info["step"]

            cycle_id = json.loads(self.redis_client.get("latest_observation"))[
                "cycle_tag"
            ]
            sample_info["cycle_tag"] = cycle_id

            try:
                with MongoClient(f"{self.mongo_client_url}") as mongo_client:
                    mongo_db = mongo_client.get_database(f"{self.mongo_db_name}")
                    mongo_coll = mongo_db.get_collection(
                        f"{self.mongo_collection_name}"
                    )
                    mongo_coll.insert_one(sample_info)

                logging.debug(f"[MongoDB] Successful entry to MongoDB")

            except Exception as ex:
                logging.error(f"[MongoDB] Error occurred: {ex}")

            continuous_fractionation_bool = get_redis_bool(
                self.redis_client, "continuous-fractionate", False
            )

            if continuous_fractionation_bool is False:
                break

        # Step 6:
        set_diverter_valve(False)

        # Step 7:
        set_redis_bool(self.redis_client, key=self.fractionate_key, value=False)

        # Step 8:
        self.global_index += 1
        advance_fc()

        return
