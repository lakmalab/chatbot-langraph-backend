import enum

class SchemeType(str, enum.Enum):
    PENSION = "pension"
    VEHICLE = "vehicle"
    CROP = "crop"
    OTHER = "other"