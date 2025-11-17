# nesting_engine.py
from dataclasses import dataclass, field

@dataclass
class Placement:
    x: float
    y: float
    width: float
    height: float
    door: str
    grain: bool


@dataclass
class Sheet:
    width: float
    height: float
    name: str
    placements: list = field(default_factory=list)

    def free_rectangles(self):
        if not self.placements:
            return [(0, 0, self.width, self.height)]

        # Start with the whole sheet
        free = [(0, 0, self.width, self.height)]

        for p in self.placements:
            new_free = []
            for fx, fy, fw, fh in free:
                # check overlap
                if not (p.x + p.width <= fx or 
                        p.x >= fx + fw or 
                        p.y + p.height <= fy or 
                        p.y >= fy + fh):

                    # Split free space around the cut
                    # Left
                    if p.x > fx:
                        new_free.append((fx, fy, p.x - fx, fh))
                    # Right
                    if p.x + p.width < fx + fw:
                        new_free.append((p.x + p.width, fy, (fx + fw) - (p.x + p.width), fh))
                    # Top
                    if p.y > fy:
                        new_free.append((fx, fy, fw, p.y - fy))
                    # Bottom
                    if p.y + p.height < fy + fh:
                        new_free.append((fx, p.y + p.height, fw, (fy + fh) - (p.y + p.height)))

                else:
                    new_free.append((fx, fy, fw, fh))

            free = new_free

        return free


def can_fit(plate, rect, allow_rotation):
    rx, ry, rw, rh = rect
    w, h = plate.width, plate.height

    if plate.grain:
        return (w <= rw and h <= rh, False)

    # rotation allowed
    normal = w <= rw and h <= rh
    rotated = h <= rw and w <= rh

    if rotated and not normal:
        return (True, True)  # fit if rotated only
    if normal:
        return (True, False) # fit normally
    return (False, False)


def place_plate(sheet, plate):
    free_rects = sheet.free_rectangles()
    best_rect = None
    best_waste = None
    rotate_flag = False

    for fr in free_rects:
        fits, rotated = can_fit(plate, fr, allow_rotation=not plate.grain)

        if not fits:
            continue

        # Wasted area = free rectangle area - plate area
        _, _, fw, fh = fr
        waste = (fw * fh) - (plate.width * plate.height)

        if best_waste is None or waste < best_waste:
            best_waste = waste
            best_rect = fr
            rotate_flag = rotated

    if best_rect is None:
        return False  # cannot place

    x, y, fw, fh = best_rect

    pw = plate.height if rotate_flag else plate.width
    ph = plate.width if rotate_flag else plate.height

    sheet.placements.append(
        Placement(
            x=x,
            y=y,
            width=pw,
            height=ph,
            door=plate.door,
            grain=plate.grain
        )
    )
    return True


def nest_plates(plates, sheets):
    unplaced = []

    # Sort plates largest-first
    plates = sorted(plates, key=lambda p: max(p.width, p.height), reverse=True)

    for p in plates:
        placed = False

        # Try offcuts and sheets in order
        for s in sheets:
            if place_plate(s, p):
                placed = True
                break

        if not placed:
            unplaced.append(p)

    return sheets, unplaced
