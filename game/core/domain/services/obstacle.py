from .cover_type import CoverType
from typing import Tuple

class Obstacle:
    def __init__(self, position: Tuple[int, int], cover_type: CoverType):
        self.position = position
        self.cover_type = cover_type
