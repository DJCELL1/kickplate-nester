import pandas as pd

class Plate:
    def __init__(self, width, height, door, grain, area=None):
        self.width = int(width)
        self.height = int(height)
        self.door = door
        self.grain = grain
        self.area = area if area else self.width * self.height
        self.sheet = None
        self.x = None
        self.y = None

def load_plate_csv(file):
    df = pd.read_csv(file)
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"door", "width", "height", "grain"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain: door,width,height,grain")

    plates = []
    for _, row in df.iterrows():
        plates.append(
            Plate(
                width=row["width"],
                height=row["height"],
                door=row["door"],
                grain=str(row["grain"]).strip().lower() == "true"
            )
        )
    return plates
