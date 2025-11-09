# game/core/domain/entities/value_objects/damage.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Damage:
    """Value Object SIMPLE para daño - SIN TIPOS COMPLEJOS"""
    amount: int
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Damage amount cannot be negative")
    
    def __str__(self) -> str:
        return f"{self.amount} damage"