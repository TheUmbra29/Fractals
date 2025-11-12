from typing import List, Optional
from ..entities.value_objects.position import Position
from ..entities.cover import CoverStructure, CoverType

class CoverSystem:
    def __init__(self):
        self.cover_structures: List[CoverStructure] = []
    
    def add_cover_structure(self, position: Position, cover_type: CoverType):
        """Añade una estructura de cobertura al mapa"""
        self.cover_structures.append(CoverStructure(position, cover_type))
    
    def get_cover_status(self, attacker_pos: Position, defender_pos: Position) -> CoverType:
        """
        Calcula el estado de cobertura del defensor contra un atacante
        Returns: CoverType indicando el nivel de protección
        """
        # Si están adyacentes, no hay cobertura efectiva
        if self._are_adjacent(attacker_pos, defender_pos):
            return CoverType.FULL  # 100% de probabilidad de daño
        
        best_cover = CoverType.FULL  # Por defecto, sin cobertura
        
        for cover in self.cover_structures:
            if cover.provides_cover_from(attacker_pos, defender_pos):
                if cover.cover_type == CoverType.FULL:
                    best_cover = CoverType.FULL  # Cobertura total prevalece
                    break
                elif cover.cover_type == CoverType.HALF:
                    best_cover = CoverType.HALF  # Cobertura parcial
        
        return best_cover
    
    def _are_adjacent(self, pos1: Position, pos2: Position) -> bool:
        """Verifica si dos posiciones son adyacentes"""
        dx = abs(pos1.x - pos2.x)
        dy = abs(pos1.y - pos2.y)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0
    
    def get_hit_probability(self, attacker_pos: Position, defender_pos: Position) -> float:
        """Calcula la probabilidad de impacto basada en cobertura"""
        cover_status = self.get_cover_status(attacker_pos, defender_pos)
        
        if cover_status == CoverType.FULL:
            return 1.0  # 100% de probabilidad
        elif cover_status == CoverType.HALF:
            return 0.5  # 50% de probabilidad
        else:
            return 0.0  # 0% de probabilidad (cobertura total)