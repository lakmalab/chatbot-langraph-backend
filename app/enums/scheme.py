from enum import Enum

class SchemeType(str, Enum):
    PENSION = "PENSION"
    VEHICLE = "vehicle"
    CROP = "crop"
    OTHER = "other"