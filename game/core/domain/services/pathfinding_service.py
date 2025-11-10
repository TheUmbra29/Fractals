from typing import List, Set, Dict, Optional, Tuple
import heapq
from ..entities.value_objects.position import Position
from ..entities.battle_entity import BattleEntity

class PathfindingService:
    """Implementa A* para rutas dinámicas que evitan obstáculos automáticamente"""
    
    @staticmethod
    def find_path(start: Position, end: Position, 
                obstacles: Set[Position], 
                entities: List[BattleEntity],
                moving_entity: BattleEntity,
                max_distance: int = 999) -> List[Position]:
        """
        Encuentra la ruta óptima usando A* considerando:
        - Obstáculos de cobertura
        - Otras entidades como bloqueos  
        - Límite de distancia máxima
        """
        
        # Si el destino está bloqueado, no hay ruta
        if not PathfindingService._is_position_available(end, obstacles, entities, moving_entity):
            return []
            
        # Estructuras para A*
        open_set = []
        came_from: Dict[Position, Optional[Position]] = {}
        g_score: Dict[Position, float] = {start: 0}
        f_score: Dict[Position, float] = {start: PathfindingService._heuristic(start, end)}
        
        heapq.heappush(open_set, (f_score[start], start))
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            # Si llegamos al destino, reconstruir ruta
            if current == end:
                return PathfindingService._reconstruct_path(came_from, current)
                
            # Si excedemos la distancia máxima, abandonar
            if g_score[current] >= max_distance:
                continue
                
            for neighbor in PathfindingService._get_neighbors(current, obstacles, entities, moving_entity):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + PathfindingService._heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No se encontró camino

    @staticmethod
    def _heuristic(a: Position, b: Position) -> int:
        """Distancia Manhattan para grid táctico"""
        return abs(a.x - b.x) + abs(a.y - b.y)

    @staticmethod
    def _get_neighbors(pos: Position, 
                      obstacles: Set[Position],
                      entities: List[BattleEntity],
                      moving_entity: BattleEntity) -> List[Position]:
        """Obtiene posiciones vecinas válidas"""
        neighbors = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Solo horizontales/verticales
        
        for dx, dy in directions:
            new_pos = Position(pos.x + dx, pos.y + dy)
            
            if PathfindingService._is_position_available(new_pos, obstacles, entities, moving_entity):
                neighbors.append(new_pos)
                
        return neighbors

    @staticmethod
    def _is_position_available(pos: Position, 
                            obstacles: Set[Position],
                            entities: List[BattleEntity],
                            moving_entity: BattleEntity) -> bool:
        """Verifica si una posición está disponible para moverse"""
        # Verificar límites del grid (8x8)
        if not (0 <= pos.x < 8 and 0 <= pos.y < 8):
            return False
            
        # Verificar obstáculos
        if pos in obstacles:
            return False
            
        # Verificar otras entidades (excepto la que se mueve)
        for entity in entities:
            if entity.id == moving_entity.id:
                continue
            if entity.position == pos and entity.stats.is_alive():
                return False
                
        return True

    @staticmethod
    def _reconstruct_path(came_from: Dict[Position, Position], 
                         current: Position) -> List[Position]:
        """Reconstruye la ruta desde el destino hasta el inicio"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]  