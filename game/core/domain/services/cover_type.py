from enum import Enum

class CoverType(Enum):
    NONE = 0
    HALF = 1
    FULL = 2
    OBSTACLE = 3

    def protection_value(self):
        if self == CoverType.NONE:
            return 0
        elif self == CoverType.HALF:
            return 0.5
        elif self == CoverType.FULL:
            return 1.0
        elif self == CoverType.OBSTACLE:
            return 1.0
        return 0
