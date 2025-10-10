from enum import Enum

class SchemeType(str, Enum):
    PENSION = "pension"
    VEHICLE = "vehicle"
    CROP = "crop"
    OTHER = "other"