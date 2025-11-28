import os
import math
from typing import Dict

VOLUME_SETTINGS = os.environ.get(
    "VOLUME_SETTINGS",
    {
        "raman_flowcell_volume": 0,
        "mv_volume": 1.2,
        "valveblock_0c": 0,
        "valveblock_1b": 0,
        "spectrouv_flowcell_volume": 0,
        "biosmbuv_flowcell_volume": 0,
        "biosmbcond_flowcell_volume": 0,
        "biosmbph_flowcell_volume": 0,
        "valveblock_7b": 0,
        "diverter_valve": 0.012,
    },
)


def calc_volume_0(settings: Dict[str, float | int]) -> float:
    raman_flowcell_volume = settings["raman_flowcell_volume"]
    valveblock_0c = settings["valveblock_0c"]

    # Tubing #0: Raman #1 to Membrane Adsorber
    length_0a = 1 + 1 / 4  # [=] in
    diameter_0a = 1 / 8  # [=] in

    length_0b = 10 + 1 / 4  # [=] in
    diameter_0b = 0.030  # [=] in

    # valveblock_0c  = 0     # P0 -> P1 -> N1 -> N0

    length_0d = 8 + 1 / 2  # [=] in
    diameter_0d = 0.030

    volume_0_imperial = (
        length_0a * math.pi / 4 * diameter_0a**2
        + length_0b * math.pi / 4 * diameter_0b**2
        + valveblock_0c
        + length_0d * math.pi / 4 * diameter_0d**2
    )

    volume_0 = 16.3871 * volume_0_imperial + raman_flowcell_volume  # [=] mL
    return volume_0


# total_volume += volume_0                    # [=] mL


def calc_volume_1(settings: Dict[str, float | int]) -> float:
    mv_volume = settings["mv_volume"]
    raman_flowcell_volume = settings["raman_flowcell_volume"]
    valveblock_1b = settings["valveblock_1b"]

    # Tubing #1:  Membrane Adsorber to Raman #2
    length_1a = 3  # [=] in
    diameter_1a = 0.030  # [=] in

    valveblock_1b = 0  # N16 -> N15 -> P15 -> P16

    length_1c = 10 + 3 / 4  # [=] in
    diameter_1c = 0.030  # [=] in

    length_1d = 1 + 1 / 4  # [=] in
    diameter_1d = 1 / 8  # [=] in

    volume_1_imperial = (
        length_1a * math.pi / 4 * diameter_1a**2
        + valveblock_1b
        + length_1c * math.pi / 4 * diameter_1c**2
        + length_1d * math.pi / 4 * diameter_1d**2
    )

    volume_1 = (
        16.3871 * volume_1_imperial + raman_flowcell_volume / 2 + mv_volume
    )  # [=] mL

    return volume_1


def calc_volume_2(settings: Dict[str, float | int]) -> float:
    spectrouv_flowcell_volume = settings["spectrouv_flowcell_volume"]
    raman_flowcell_volume = settings["raman_flowcell_volume"]

    # Tubing #2: Raman #2 to Spectro UV
    length_2a = 1 + 1 / 4  # [=] in
    diameter_2a = 1 / 8  # [=] in

    length_2b = 12  # [=] in
    diameter_2b = 0.030  # [=] in

    volume_2_imperial = (
        length_2a * math.pi / 4 * diameter_2a**2
        + length_2b * math.pi / 4 * diameter_2b**2
        + spectrouv_flowcell_volume / 2
    )

    volume_2 = (
        16.3871 * volume_2_imperial
        + raman_flowcell_volume / 2
        + spectrouv_flowcell_volume / 2
    )  # [=] mL

    return volume_2


def calc_volume_3(settings: Dict[str, float | int]) -> float:
    spectrouv_flowcell_volume = settings["spectrouv_flowcell_volume"]

    # Tubing #3: Spectro UV to BioSMB UV
    length_3a = 18  # [=] in
    diameter_3a = 0.030  # [=] in

    volume_3_imperial = length_3a * math.pi / 4 * diameter_3a**2

    volume_3 = 16.3871 * volume_3_imperial + spectrouv_flowcell_volume / 2  # [=] mL

    return volume_3


def calc_volume_4(settings: Dict[str, float | int]) -> float:
    biosmbuv_flowcell_volume = settings["biosmbuv_flowcell_volume"]

    # Tubing #4: BioSMB UV DeadVolume
    length_4a = 10  # [=] in
    diameter_4a = 0.030  # [=] in

    length_4b = 4  # [=] in
    diameter_4b = 0.030  # [=] in

    length_4c = 6  # [=] in
    diameter_4c = 0.030  # [=] in

    volume_4_imperial = (
        length_4a * math.pi / 4 * diameter_4a**2
        + length_4b * math.pi / 4 * diameter_4b**2
        + length_4c * math.pi / 4 * diameter_4c**2
    )

    volume_4 = 16.3871 * volume_4_imperial + 4 * biosmbuv_flowcell_volume

    return volume_4


def calc_volume_5(settings: Dict[str, float | int]) -> float:
    biosmbph_flowcell_volume = settings["biosmbph_flowcell_volume"]

    # Tubing #5: BioSMB UV to pH Sensor
    length_5a = 13 + 1 / 2  # [=] in
    diameter_5a = 0.030  # [=] in

    volume_5_imperial = length_5a * math.pi / 4 * diameter_5a**2

    volume_5 = 16.3871 * volume_5_imperial + biosmbph_flowcell_volume  # [=] mL

    return volume_5


def calc_volume_6(settings: Dict[str, float | int]) -> float:
    biosmbcond_flowcell_volume = settings["biosmbcond_flowcell_volume"]

    # Tubing #6: pH sensor to conductivity sensor
    length_6a = 10  # [=] in
    diameter_6a = 0.030  # [=] in

    volume_6_imperial = length_6a * math.pi / 4 * diameter_6a**2

    volume_6 = 16.3871 * volume_6_imperial + biosmbcond_flowcell_volume  # [=] mL

    return volume_6


def calc_volume_7(settings: Dict[str, float | int]) -> float:
    valveblock_7b = settings["valveblock_7b"]

    # Tubing #7: Conductivity sensor to VB (O16)
    length_7a = 14  # [=] in
    diameter_7a = 0.030  # [=] in

    valveblock_7b = 0  # O16 -> O11 -> Q11

    volume_7_imperial = length_7a * math.pi / 4 * diameter_7a**2 + valveblock_7b

    volume_7 = 16.3871 * volume_7_imperial

    return volume_7


def calc_volume_8(settings: Dict[str, float | int]) -> float:
    # Tubing #8: From VB to Diverter Valve
    length_8 = 63.5  # [=] in
    diameter_8 = 1 / 16  # [=] in

    volume_8_imperial = math.pi * diameter_8**2 * length_8 / 4  # [=] in^3

    volume_8 = 16.3871 * volume_8_imperial  # [=] mL

    return volume_8


def calc_volume_9(settings: Dict[str, float | int]) -> float:
    diverter_valve = settings["diverter_valve"]
    # Tubing #9: Diverter Valve
    volume_9 = diverter_valve  # [=] mL

    return volume_9


def calc_volume_10(settings: Dict[str, float | int]) -> float:
    # Tubing #10: Diverter Valve to Deep Well Plate
    length_10 = 25.5  # [=] in
    diameter_10 = 1 / 16  # [=] in

    volume_10_imperial = math.pi * diameter_10**2 * length_10 / 4  # [=] in^3

    volume_10 = 16.3871 * volume_10_imperial  # [=] mL

    return volume_10


def get_divertervalve_collection_dv():
    return calc_volume_10(VOLUME_SETTINGS) + calc_volume_9(VOLUME_SETTINGS)


def get_biosmb_to_divertervalve_dv():
    return calc_volume_8(VOLUME_SETTINGS)


def calculate_deadvolume():
    total_volume = 0

    total_volume += calc_volume_0(VOLUME_SETTINGS)
    total_volume += calc_volume_1(VOLUME_SETTINGS)
    total_volume += calc_volume_2(VOLUME_SETTINGS)
    total_volume += calc_volume_3(VOLUME_SETTINGS)
    total_volume += calc_volume_4(VOLUME_SETTINGS)
    total_volume += calc_volume_5(VOLUME_SETTINGS)
    total_volume += calc_volume_6(VOLUME_SETTINGS)
    total_volume += calc_volume_7(VOLUME_SETTINGS)
    total_volume += calc_volume_8(VOLUME_SETTINGS)
    total_volume += calc_volume_9(VOLUME_SETTINGS)
    total_volume += calc_volume_10(VOLUME_SETTINGS)

    return round(total_volume, 3)


if __name__ == "__main__":
    print(f"get_biofrac_dv(): \t{get_divertervalve_collection_dv()}")
