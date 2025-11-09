from ..entities.battle_entity import BattleEntity

class ExperienceService:
    """Servicio para gestionar experiencia y progresión temporal"""
    
    @staticmethod
    def calculate_experience_reward(enemy_level: int, player_level: int) -> int:
        """Calcula experiencia basada en diferencia de niveles"""
        base_exp = 50
        level_diff = enemy_level - player_level
        
        if level_diff > 0:
            return base_exp + (level_diff * 10)  # Bonus por enemigo más fuerte
        else:
            return max(10, base_exp + (level_diff * 5))  # Reducción por enemigo más débil
    
    @staticmethod
    def apply_level_up_benefits(entity: BattleEntity) -> None:
        """Aplica beneficios al subir de nivel (simple)"""
        # Por ahora, solo aumentamos stats básicos
        # En el futuro podría ser más complejo
        old_stats = entity.stats
        # Aquí iría la lógica para mejorar stats
        # Por simplicidad, no implementamos cambios aún
        pass