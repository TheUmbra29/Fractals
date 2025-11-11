from typing import Set, List
from ..entities.battle_entity import BattleEntity
from ..entities.value_objects.position import Position
from ..entities.value_objects.game_enums import Team

class MovementValidationService:
    """Servicio para validar movimientos en FRACTALS"""
    
    @staticmethod
    def validate_movement_path(start: Position, end: Position, obstacles: Set[Position], entities: List[BattleEntity]) -> bool:
        """Valida movimiento usando enums"""
        for entity in entities:
            if entity.position == end and entity.team == Team.PLAYER:  # Solo aliados bloquean
                return False
        if end in obstacles:
            return False
        return True
    
    @staticmethod
    def get_valid_movement_positions(entity: BattleEntity, movement_range: int, obstacles: Set[Position], all_entities: List[BattleEntity]) -> Set[Position]:
        """Obtiene posiciones válidas para movimiento (simplificado)"""
        valid_positions = set()
        start = entity.position
        
        # Simple generación de posiciones en un cuadrado
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                if abs(dx) + abs(dy) <= movement_range:  # Distancia Manhattan
                    new_pos = Position(start.x + dx, start.y + dy)
                    
                    # Validar posición
                    if MovementValidationService.validate_movement_path(start, new_pos, obstacles, all_entities):
                        valid_positions.add(new_pos)
        
        return valid_positions