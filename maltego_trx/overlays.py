from enum import Enum


class OverlayPosition(Enum):
    NORTH = "N"
    SOUTH = "S"
    WEST = "W"
    NORTH_WEST = "NW"
    SOUTH_WEST = "SW"
    CENTER = "C"


class OverlayType(Enum):
    IMAGE = "image"
    COLOUR = "colour"
    TEXT = "text"
