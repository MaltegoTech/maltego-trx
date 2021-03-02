from enum import Enum


class Position(Enum):
    NORTH = "N"
    NORTH_EAST = "NE"
    NORTH_WEST = "NW"
    EAST = "E"
    CENTER = "C"
    WEST = "W"
    SOUTH = "S"
    SOUTH_EAST = "SE"
    SOUTH_WEST = "SW"


class OverlayType(Enum):
    IMAGE = "image"
    COLOUR = "colour"
    TEXT = "text"
