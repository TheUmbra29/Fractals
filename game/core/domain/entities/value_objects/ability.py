from dataclasses import dataclass
from typing import Dict, Any, Optional
from .ability_id import AbilityId

@dataclass(frozen=True)
class Ability:
    """Value Object para representar una habilidad con PH y TdE"""
    id: AbilityId
    name: str
    description: str
    ph_cost: int
    cooldown_turns: int
    current_cooldown: int = 0
    ability_type: str = "active"  # "active", "passive", "ultimate"
    damage_multiplier: float = 1.0
    range: int = 1
    
    def is_available(self, current_ph: int) -> bool:
        """Verifica si la habilidad puede usarse"""
        return (current_ph >= self.ph_cost and 
                self.current_cooldown <= 0)
    
    def use(self) -> 'Ability':
        """Retorna una nueva instancia con cooldown aplicado"""
        return Ability(
            id=self.id,
            name=self.name,
            description=self.description,
            ph_cost=self.ph_cost,
            cooldown_turns=self.cooldown_turns,
            current_cooldown=self.cooldown_turns,
            ability_type=self.ability_type,
            damage_multiplier=self.damage_multiplier,
            range=self.range
        )
    
    def reduce_cooldown(self) -> 'Ability':
        """Reduce el cooldown en 1 turno"""
        new_cooldown = max(0, self.current_cooldown - 1)
        return Ability(
            id=self.id,
            name=self.name,
            description=self.description,
            ph_cost=self.ph_cost,
            cooldown_turns=self.cooldown_turns,
            current_cooldown=new_cooldown,
            ability_type=self.ability_type,
            damage_multiplier=self.damage_multiplier,
            range=self.range
        )