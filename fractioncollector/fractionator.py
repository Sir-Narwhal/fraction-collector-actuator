from typing import Dict
from .mapping import PositionMapping
from .plate import Plate
from .well import Well


class FractionCollector:
    def __init__(self, num_plates: int = 4, wells_per_plate: int = 96, prefix="fc"):
        self.num_plates = num_plates
        self.wells_per_plate = wells_per_plate
        self.prefix = prefix
        self.plates = [Plate(i, wells_per_plate) for i in range(num_plates)]
        self.mapping = self._build_position_mapping()

    def _build_position_mapping(self):
        mapping = {}
        total_positions = self.num_plates * self.wells_per_plate

        for pos in range(1, total_positions + 1):
            plate_idx = (pos - 1) // self.wells_per_plate
            well_idx = (pos - 1) % self.wells_per_plate

            plate = self.plates[plate_idx]
            well_name = plate.wells[well_idx]

            well_obj = Well(plate.name, well_name, self.prefix)
            mapping[pos] = {
                "plate": plate.name,
                "well": well_name,
                "unique_id": well_obj.unique_id,
            }

        return PositionMapping(mapping)

    def get_actual_plate_info(self, global_index: int) -> Dict[str, object]:
        """Will provide unique metadata for global position of fraction collector.
            This unique data includes a track of plate position, plate number, well number,
            and a unqiue id that can be found to correlate with MongoDB.

        Args:
            global_index (int): provides the global index of advancement in 96 well plates of entire experiment
        """

        actual_plate_number = (global_index - 1) // self.wells_per_plate + 1
        actual_plate_name = f"plate{actual_plate_number:04d}"

        physical_plate_number = ((actual_plate_number - 1) % self.num_plates) + 1
        plate_obj = self.plates[physical_plate_number]

        well_idx = (global_index - 1) % self.wells_per_plate
        well_name = plate_obj.wells[well_idx]

        unique_id = f"{self.prefix}-sample{actual_plate_name}-positional{plate_obj.name}-well{well_name}"

        return {
            "global_index": global_index,
            "sample_plate": actual_plate_name,
            "positional_plate": plate_obj.name,
            "well": well_name,
            "unique_id": unique_id,
        }
