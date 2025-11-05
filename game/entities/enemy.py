from game.entities.battle_entity import BattleEntity

class Enemy(BattleEntity):  # 🆕 HEREDA DE BATTLEENTITY
    """Enemigo - ahora usa BattleEntity unificada"""
    
    def __init__(self, position, team="enemy", name="Enemigo"):
        # 🎯 CONSTRUCTOR SIMPLIFICADO - BattleEntity maneja todo
        super().__init__(
            name=name,
            position=position,
            team=team,
            stats=self._get_enemy_stats(name),
            character_class="enemy",
            abilities_config=self._get_enemy_abilities()
        )
    
    def _get_enemy_stats(self, name):
        """Stats base para enemigos"""
        return {
            'max_hp': 80,
            'current_hp': 80,
            'max_ph': 50,
            'current_ph': 50,
            'attack': 12,
            'defense': 5,
            'speed': 4,
            'max_energy': 0  # Enemigos no usan energía por ahora
        }
    
    def _get_enemy_abilities(self):
        """Habilidades básicas para enemigos"""
        return {
            "basic_attack": {
                "name": "Ataque Básico",
                "cost_ph": 0,
                "range": 1,
                "selection_mode": "enemy",
                "effects": [
                    {
                        "type": "damage",
                        "multiplier": 1.0,
                        "damage_type": "physical"
                    }
                ]
            }
        }
    
    def setup_energy_listeners(self):
        """Enemigos no necesitan listeners de energía"""
        pass  # No hacer nada - los enemigos no ganan energía
    
    def gain_energy(self, amount, source="unknown"):
        """Enemigos no ganan energía"""
        pass  # No hacer nada
    
    def can_use_ultimate(self, ability_config):
        """Enemigos no pueden usar ultimates"""
        return False
    
    def consume_ultimate_energy(self, energy_cost):
        """Enemigos no consumen energía"""
        return False