from enum import Enum
from typing import List
from .value_objects.position import Position

class CoverType(Enum):
    FULL = "full"      # Cuadrado (muro alto)
    HALF = "half"      # Medio cuadrado (muro chiquito)

class CoverStructure:
    def __init__(self, position: Position, cover_type: CoverType):
        self.position = position
        self.cover_type = cover_type
        self.health = 100  # Opcional: para estructuras destructibles
        
    def provides_cover_from(self, attacker_pos: Position, defender_pos: Position) -> bool:
        """Determina si esta estructura protege al defensor del atacante"""
        # Verificar si la estructura está entre el atacante y defensor
        return self._is_between_positions(attacker_pos, defender_pos, self.position)
    
    def _is_between_positions(self, pos1: Position, pos2: Position, check_pos: Position) -> bool:
        """Verifica si check_pos está entre pos1 y pos2"""
        # Simplificado: verificar si está en la línea de visión
        min_x, max_x = sorted([pos1.x, pos2.x])
        min_y, max_y = sorted([pos1.y, pos2.y])
        
        return (min_x <= check_pos.x <= max_x and 
                min_y <= check_pos.y <= max_y and
                self._is_in_line_of_sight(pos1, pos2, check_pos))
    
    def _is_in_line_of_sight(self, pos1: Position, pos2: Position, check_pos: Position) -> bool:
        """Verifica si check_pos está en la línea entre pos1 y pos2"""
        # Algoritmo básico de línea de visión
        if pos1.x == pos2.x:  # Misma columna
            return check_pos.x == pos1.x
        elif pos1.y == pos2.y:  # Misma fila
            return check_pos.y == pos1.y
        else:
            # Para diagonales, verificar pendiente
            slope = (pos2.y - pos1.y) / (pos2.x - pos1.x)
            expected_y = pos1.y + slope * (check_pos.x - pos1.x)
            return abs(check_pos.y - expected_y) < 0.5
