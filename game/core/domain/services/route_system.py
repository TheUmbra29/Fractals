from typing import List, Set
from ..entities.value_objects.position import Position
from ..entities.battle_entity import BattleEntity
from ..entities.aggregates.battle import Battle
from .pathfinding_service import PathfindingService

class MovementRoute:
    """Value Object que representa una ruta completa con embestidas"""
    
    def __init__(self, path: List[Position], dash_targets: List[BattleEntity], is_valid: bool = True):
        self.path = path
        self.dash_targets = dash_targets
        self.is_valid = is_valid
        self.total_distance = len(path)
        self.dash_damage = len(dash_targets) * 15  # 15 daño fijo por embestida

class RouteSystem:
    """Sistema que calcula rutas y detecta embestidas automáticamente"""
    
    @staticmethod
    def calculate_route(start: Position, end: Position, battle: Battle, moving_entity: BattleEntity) -> MovementRoute:
        """Calcula ruta y detecta enemigos en el camino para embestidas"""
        
        # Calcular ruta con A*
        path = PathfindingService.find_path(
            start, end,
            battle._obstacles,
            list(battle._entities.values()),
            moving_entity
        )
        
        if not path:
            return MovementRoute([], [], False)
            
        # Detectar enemigos para embestidas a lo largo de la ruta
        dash_targets = RouteSystem._find_dash_targets_along_route(path, battle, moving_entity)
        
        # Validar límite de velocidad
        is_valid = len(path) <= 999
        
        return MovementRoute(path, dash_targets, is_valid)
    
    @staticmethod
    def _find_dash_targets_along_route(route: List[Position], battle: Battle, moving_entity: BattleEntity) -> List[BattleEntity]:
        """Encuentra enemigos adyacentes a la ruta para embestidas"""
        dash_targets = []
        visited_enemies = set()
        
        for position in route:
            # Buscar enemigos adyacentes a esta posición de la ruta
            adjacent_positions = [
                Position(position.x + 1, position.y),
                Position(position.x - 1, position.y), 
                Position(position.x, position.y + 1),
                Position(position.x, position.y - 1)
            ]
            
            for adj_pos in adjacent_positions:
                enemy = battle.get_entity_at_position(adj_pos)
                if (enemy and 
                    enemy.team != moving_entity.team and 
                    enemy.stats.is_alive() and
                    enemy.id not in visited_enemies):
                    dash_targets.append(enemy)
                    visited_enemies.add(enemy.id)
                    
        return dash_targets