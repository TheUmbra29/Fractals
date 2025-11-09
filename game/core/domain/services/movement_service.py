from typing import List, Set
from ..entities.battle_entity import BattleEntity
from ..entities.value_objects.position import Position
from ..entities.value_objects.entity_id import EntityId

class MovementService:
    """Servicio de dominio para movimiento y embestidas en FRACTALS"""

    @staticmethod
    def calculate_dash_damage(entity: BattleEntity) -> int:
        return max(1, int(entity.stats.attack * 0.1))  # 10% del ataque

    @staticmethod
    def validate_dash_target(dasher: BattleEntity, target: BattleEntity) -> bool:
        # Verificar que el objetivo no haya sido embestido en este movimiento
        return target.id not in dasher.dash_targets_this_move

    @staticmethod
    def get_adjacent_positions(position: Position) -> List[Position]:
        return position.adjacent_positions()

    @staticmethod
    def calculate_path(start: Position, end: Position, obstacles: Set[Position]) -> List[Position]:
        # Implementación simple de camino (podría ser A* en el futuro)
        # Por ahora, devolvemos una línea recta (sin obstáculos)
        path = []
        current = start
        while current != end:
            # Movimiento en una dirección a la vez
            if current.x < end.x:
                current = Position(current.x + 1, current.y)
            elif current.x > end.x:
                current = Position(current.x - 1, current.y)
            elif current.y < end.y:
                current = Position(current.x, current.y + 1)
            elif current.y > end.y:
                current = Position(current.x, current.y - 1)
            path.append(current)
            # Si encontramos un obstáculo, rompemos (por simplicidad)
            if current in obstacles:
                break
        return path