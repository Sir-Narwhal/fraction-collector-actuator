from fractioncollector.fractionator import FractionCollector

if __name__ == "__main__":
    fc = FractionCollector()

    info = fc.get_actual_plate_info(127001)

    print(info)
