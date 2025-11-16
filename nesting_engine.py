class Sheet:
    def __init__(self, width, height, name):
        self.width = width
        self.height = height
        self.name = name
        self.shelves = []
        self.placements = []

def shelf_nest(plates, sheets, allow_rotation=True):
    plates = sorted(plates, key=lambda p: max(p.width, p.height), reverse=True)

    unplaced = []

    for plate in plates:
        placed = False

        for sheet in sheets:
            for shelf in sheet.shelves:
                if (plate.grain is False and allow_rotation and plate.height <= shelf["height"] and plate.width <= shelf["space"]) \
                   or (plate.width <= shelf["space"] and plate.height <= shelf["height"]):
                    plate.x = shelf["used"]
                    plate.y = shelf["y"]
                    plate.sheet = sheet.name

                    shelf["used"] += plate.width
                    shelf["space"] -= plate.width

                    sheet.placements.append(plate)
                    placed = True
                    break
            if placed:
                break

            # Try creating a new shelf
            used_height = sum([s["height"] for s in sheet.shelves])
            if used_height + plate.height <= sheet.height:
                shelf = {
                    "y": used_height,
                    "height": plate.height,
                    "used": plate.width,
                    "space": sheet.width - plate.width
                }
                sheet.shelves.append(shelf)

                plate.x = 0
                plate.y = used_height
                plate.sheet = sheet.name
                sheet.placements.append(plate)
                placed = True
                break

        if not placed:
            unplaced.append(plate)

    return sheets, unplaced
