from dataclasses import dataclass
from typing import Any, List

@dataclass(frozen=True)
class Position:
    """Value Object - INMUTABLE para posiciones en grid"""
    x: int
    y: int
    
    def __post_init__(self):
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise ValueError("Position coordinates must be integers")
    
    # ✅ AGREGAR ESTOS MÉTODOS PARA HACER POSITION COMPARABLE
    def __lt__(self, other: Any) -> bool:
        """Permite comparar Position para ordenamiento (necesario para A*)"""
        if not isinstance(other, Position):
            return NotImplemented
        # Ordenar primero por x, luego por y
        return (self.x, self.y) < (other.x, other.y)
    
    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.x, self.y) <= (other.x, other.y)
    
    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.x, self.y) > (other.x, other.y)
    
    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.x, self.y) >= (other.x, other.y)
    
    # Los métodos existentes...
    def distance_to(self, other: 'Position') -> int:
        """Distancia Manhattan para movimiento táctico"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def adjacent_positions(self) -> List['Position']:
        """Posiciones adyacentes (para movimiento y ataques)"""
        return [
            Position(self.x + 1, self.y),
            Position(self.x - 1, self.y), 
            Position(self.x, self.y + 1),
            Position(self.x, self.y - 1)
        ]
    
    def is_within_grid(self, grid_size: tuple) -> bool:
        """Verifica si la posición está dentro del grid"""
        return (0 <= self.x < grid_size[0] and 
                0 <= self.y < grid_size[1])
    
    @staticmethod
    def line_between(start: 'Position', end: 'Position') -> List['Position']:
        """Genera posiciones en línea recta entre dos puntos (simplificado)"""
        positions = []
        current = start
        
        while current != end:
            if current.x < end.x:
                current = Position(current.x + 1, current.y)
            elif current.x > end.x:
                current = Position(current.x - 1, current.y)
            elif current.y < end.y:
                current = Position(current.x, current.y + 1)
            elif current.y > end.y:
                current = Position(current.x, current.y - 1)
            positions.append(current)
            
        return positions
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"