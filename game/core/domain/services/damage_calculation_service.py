from ..config.game_config import GAME_CONFIG

class DamageCalculationService:
    """Servicio centralizado para cálculos de daño"""
    
    @staticmethod
    def calculate_basic_attack_damage(attacker, defender) -> int:
        """Calcula daño usando stats reales en lugar de hardcode"""
        base_damage = max(1, attacker.stats.attack - (defender.stats.defense // 2))
        return base_damage
    
    @staticmethod
    def calculate_ability_damage(attacker, defender, multiplier: float) -> int:
        """Calcula daño de habilidad"""
        damage = int(attacker.stats.attack * multiplier) - (defender.stats.defense // 2)
        return max(1, damage)
    
    @staticmethod
    def calculate_dash_damage() -> int:
        """Daño de embestida desde configuración"""
        return GAME_CONFIG.BASE_DASH_DAMAGE