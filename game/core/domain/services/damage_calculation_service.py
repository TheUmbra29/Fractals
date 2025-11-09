from ..entities.battle_entity import BattleEntity

class DamageCalculationService:
    """Servicio SIMPLE para calcular daño - SIN COMPLEJIDADES"""
    
    @staticmethod
    def calculate_basic_attack_damage(attacker: BattleEntity, defender: BattleEntity) -> int:
        """Daño básico: ataque - (defensa / 2)"""
        damage = attacker.stats.attack - (defender.stats.defense // 2)
        return max(1, damage)  # Mínimo 1 de daño
    
    @staticmethod
    def calculate_ability_damage(attacker: BattleEntity, defender: BattleEntity, multiplier: float) -> int:
        """Daño de habilidad: (ataque * multiplicador) - (defensa / 2)"""
        damage = int(attacker.stats.attack * multiplier) - (defender.stats.defense // 2)
        return max(1, damage)
    
    @staticmethod
    def calculate_dash_damage(attacker: BattleEntity) -> int:
        """Daño de embestida: 10% del ataque"""
        return max(1, int(attacker.stats.attack * 0.1))