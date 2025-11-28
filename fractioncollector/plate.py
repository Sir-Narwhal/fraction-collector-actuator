import string


class Plate:
    def __init__(self, index: int, wells_per_plate: int = 96):
        self.index = index
        self.wells_per_plate = wells_per_plate
        self.wells = self._generate_wells()

    def _generate_wells(self):
        rows = list(string.ascii_uppercase[:8])
        cols = [f"{i:02d}" for i in range(1, 13)]

        wells = []
        for i, row in enumerate(rows):
            if i > 0:
                cols.reverse()
            wells.extend([f"{row}{c}" for c in cols])

        return wells

    def get_well(self, well_index: int):
        return self.wells[well_index]

    @property
    def name(self):
        return f"plate{self.index+1}"
