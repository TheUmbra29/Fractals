from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class Progression:
    """Value Object para la progresión temporal de FRACTALS (se reinicia cada sesión)"""
    level: int = 1
    experience: int = 0
    temporary_bonuses: Dict[str, int] = field(default_factory=dict)

    def add_experience(self, amount: int) -> 'Progression':
        new_experience = self.experience + amount
        new_level = self.level
        # Lógica simple de nivelación: cada 100 puntos de experiencia sube de nivel
        if new_experience >= new_level * 100:
            new_level += 1
            new_experience = 0  # Reiniciamos la experiencia al subir de nivel
        return Progression(level=new_level, experience=new_experience, temporary_bonuses=self.temporary_bonuses.copy())

    def add_temporary_bonus(self, stat: str, value: int) -> 'Progression':
        new_bonuses = self.temporary_bonuses.copy()
        new_bonuses[stat] = new_bonuses.get(stat, 0) + value
        return Progression(level=self.level, experience=self.experience, temporary_bonuses=new_bonuses)