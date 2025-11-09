from ..entities.battle_entity import BattleEntity
from ..entities.value_objects.position import Position

class CoverSystem:
    """Sistema de cobertura SIMPLE para FRACTALS - CON LÍMITES DEL GRID"""
    
    @staticmethod
    def has_cover(entity: BattleEntity, obstacles: set, grid_size: tuple = (8, 8)) -> bool:
        """Verifica si una entidad tiene cobertura, considerando límites del grid"""
        for adjacent_pos in entity.position.adjacent_positions():
            # Verificar que la posición adyacente esté dentro del grid
            if (0 <= adjacent_pos.x < grid_size[0] and 
                0 <= adjacent_pos.y < grid_size[1] and
                adjacent_pos in obstacles):
                return True
        return False
    
    @staticmethod
    def get_cover_defense_bonus() -> int:
        """Bonus de defensa por tener cobertura"""
        return 20  # +20 defensa simple