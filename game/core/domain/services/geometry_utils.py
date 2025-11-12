from typing import Tuple

class GeometryUtils:
    @staticmethod
    def midpoint(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
        return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)

    @staticmethod
    def is_between(start: Tuple[int, int], end: Tuple[int, int], obstacle_pos: Tuple[int, int]) -> bool:
        x1, y1 = start
        x2, y2 = end
        ox, oy = obstacle_pos
        if (min(x1, x2) < ox < max(x1, x2) or min(y1, y2) < oy < max(y1, y2)):
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0:
                return ox == x1 and min(y1, y2) < oy < max(y1, y2)
            if dy == 0:
                return oy == y1 and min(x1, x2) < ox < max(x1, x2)
            if abs(dx) == abs(dy):
                return abs(ox - x1) == abs(oy - y1) and min(x1, x2) < ox < max(x1, x2)
        return False

    @staticmethod
    def blocks_line_of_sight(start: Tuple[int, int], end: Tuple[int, int], obstacle_pos: Tuple[int, int]) -> bool:
        return obstacle_pos == GeometryUtils.midpoint(start, end)
