from typing import Dict


class PositionMapping:
    """Maps fraction collector positions (plate, well, and unique id) will also support reverse lookup for well id"""

    def __init__(self, mapping: Dict):
        self.mapping = mapping

    def get_by_position(self, position: int):
        return self.mapping[position]

    def find_position(self, plate_name: str, well_name: str):
        for pos, info in self.mapping.items():
            if info["plate"] == plate_name and info["well"] == well_name:
                return pos
        raise KeyError(f"No match for {plate_name} {well_name}")
