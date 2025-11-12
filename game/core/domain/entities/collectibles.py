from enum import Enum, auto
from core.domain.entities.value_objects.position import Position

class CollectibleType(Enum):
    ENERGY = auto()
    HP = auto()
    PH = auto()
    XP = auto()

class Collectible:
    def __init__(self, position: Position, type_: CollectibleType, base_value: int, cooldown: int, level: int = 1):
        self.position = position
        self.type = type_
        self.base_value = base_value
        self.cooldown = cooldown
        self.level = level
        self.turns_active = 0
        self.turns_on_cooldown = 0

    def is_available(self):
        return self.turns_on_cooldown == 0

    def advance_turn(self):
        if self.turns_on_cooldown > 0:
            self.turns_on_cooldown -= 1
            self.level = 1  # Vuelve al nivel más bajo
        else:
            self.turns_active += 1
            # HP y XP suben de nivel según reglas
            if self.type in [CollectibleType.HP, CollectibleType.XP]:
                if self.type == CollectibleType.HP and self.turns_active > 0:
                    self.level = min(3, self.level + 1)
                if self.type == CollectibleType.XP and self.turns_active >= 2:
                    self.level = min(3, self.level + 1)

    def collect(self, entity, multiplier=1.0):
        if not self.is_available():
            return False, "Cápsula en TdE"
        value = self.get_effective_value(multiplier)
        if self.type == CollectibleType.ENERGY:
            # Recarga definitiva
            entity.recharge_ultimate(value)
        elif self.type == CollectibleType.HP:
            entity.restore_hp(value)
        elif self.type == CollectibleType.PH:
            entity.restore_ph(value)
        elif self.type == CollectibleType.XP:
            entity.gain_experience(value)
        self.turns_on_cooldown = self.cooldown
        self.turns_active = 0
        self.level = 1
        return True, f"{self.type.name} recogida: +{value}"

    def get_effective_value(self, multiplier=1.0):
        # Valores por nivel
        if self.type == CollectibleType.HP:
            return int(self.base_value * [1, 1, 2, 4][self.level] * multiplier)
        if self.type == CollectibleType.XP:
            return int(self.base_value * [1, 1, 2, 4][self.level] * multiplier)
        if self.type == CollectibleType.ENERGY:
            return int(self.base_value * multiplier)
        if self.type == CollectibleType.PH:
            return int(self.base_value)
        return 0
