from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EntityStats:
    """Value Object - INMUTABLE para estadísticas de entidades"""
    max_hp: int
    current_hp: int
    max_ph: int  
    current_ph: int
    attack: int
    defense: int
    speed: int
    
    def __post_init__(self):
        # Validaciones de integridad
        if any(valor < 0 for valor in [self.max_hp, self.current_hp, self.max_ph, 
                                      self.current_ph, self.attack, self.defense, self.speed]):
            raise ValueError("Stats cannot be negative")
        
        if self.current_hp > self.max_hp:
            raise ValueError("Current HP cannot exceed Max HP")
            
        if self.current_ph > self.max_ph:
            raise ValueError("Current PH cannot exceed Max PH")
    
    def reduce_hp(self, amount: int) -> 'EntityStats':
        """Devuelve NUEVO objeto con HP reducido - INMUTABLE"""
        new_hp = max(0, self.current_hp - amount)
        return EntityStats(
            max_hp=self.max_hp,
            current_hp=new_hp,
            max_ph=self.max_ph,
            current_ph=self.current_ph,
            attack=self.attack,
            defense=self.defense,
            speed=self.speed
        )
    
    def reduce_ph(self, amount: int) -> 'EntityStats':
        """Devuelve NUEVO objeto con PH reducido - INMUTABLE"""
        new_ph = max(0, self.current_ph - amount)
        return EntityStats(
            max_hp=self.max_hp,
            current_hp=self.current_hp,
            max_ph=self.max_ph,
            current_ph=new_ph,
            attack=self.attack,
            defense=self.defense,
            speed=self.speed
        )
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def hp_percentage(self) -> float:
        return (self.current_hp / self.max_hp) * 100 if self.max_hp > 0 else 0