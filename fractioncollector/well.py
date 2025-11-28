class Well:
    def __init__(self, plate_name: str, well_name: str, prefix="fc"):
        self.plate_name = plate_name
        self.well_name = well_name
        self.prefix = prefix

    @property
    def unique_id(self):
        return f"{self.prefix}_{self.plate_name}_well{self.well_name}"

    def __repr__(self):
        return f"<well {self.unique_id}>"
