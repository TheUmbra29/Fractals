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
    """Sistema simplificado para rutas con puntos de anclaje"""

    @staticmethod
    def calculate_route_with_anchors(start: Position, destination: Position,
                                     anchors: List[Position], battle, # Battle import moved inside
                                     moving_entity: BattleEntity) -> MovementRoute:
        """
        Calcula ruta que pasa por todos los puntos de anclaje en orden
        A → Anchor1 → Anchor2 → ... → Destination
        """
        # Importación local para evitar ciclo
        from ..entities.aggregates.battle import Battle
        all_points = [start] + anchors + [destination]
        full_path = []

        # Calcular ruta por segmentos
        for i in range(len(all_points) - 1):
            segment_start = all_points[i]
            segment_end = all_points[i + 1]

            # ✅ ACTUALIZADO CRÍTICO: Usar is_preview=True para previsualización
            segment = PathfindingService.find_path(
                segment_start, segment_end,
                battle.get_obstacles(),
                battle.get_entities(),
                moving_entity,
                is_preview=True  # ✅ MODO PREVISUALIZACIÓN - ignora enemigos
            )

            if not segment:
                return MovementRoute([], [], False)

            # Añadir segmento a la ruta completa
            if full_path:
                full_path.extend(segment[1:])
            else:
                full_path.extend(segment)

        # Encontrar entidades en las posiciones de anclaje
        dash_targets = []
        for anchor_pos in anchors:
            enemy = battle.get_entity_at_position(anchor_pos)
            if enemy and enemy.team != moving_entity.team:
                dash_targets.append(enemy)

        return MovementRoute(full_path, dash_targets, True)