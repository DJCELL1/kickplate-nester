import pandas as pd

COLUMN_MAP = {
    "door": ["door", "doorno", "doornumber", "door_number", "d", "doors"],
    "width": ["width", "w", "platewidth", "plate_width"],
    "height": ["height", "h", "plateheight", "plate_height"],
    "grain": ["grain", "graindirection", "grain_required", "g", "grainreq"]
}

def normalise_columns(df):
    new_cols = {}
    for c in df.columns:
        clean = (
            str(c)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )
        new_cols[c] = clean
    df.rename(columns=new_cols, inplace=True)
    return df

def find_column(df, target):
    mapping = COLUMN_MAP[target]
    for col in df.columns:
        if col in mapping:
            return col
    return None

class Plate:
    def __init__(self, width, height, door, grain, area=None):
        self.width = int(width)
        self.height = int(height)
        self.door = str(door)
        self.grain = bool(grain)
        self.area = area if area else self.width * self.height
        self.sheet = None
        self.x = None
        self.y = None

def load_plate_csv(file):
    df = pd.read_csv(file)
    df = normalise_columns(df)

    door_col = find_column(df, "door")
    width_col = find_column(df, "width")
    height_col = find_column(df, "height")
    grain_col = find_column(df, "grain")

    if None in [door_col, width_col, height_col, grain_col]:
        raise ValueError(f"""
CSV is missing one of the required columns:
- door
- width
- height
- grain

We detected columns: {list(df.columns)}
""")

    plates = []
    for _, row in df.iterrows():
        grain_value = str(row[grain_col]).lower().strip() in ("true", "1", "yes", "y")
        plates.append(
            Plate(
                width=row[width_col],
                height=row[height_col],
                door=row[door_col],
                grain=grain_value
            )
        )
    return plates
