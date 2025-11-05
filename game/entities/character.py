from .game_entity import GameEntity
from game.systems.action_system.move_action import MoveAction

class Character(GameEntity):
    """Personaje jugable - hereda de GameEntity CORREGIDO"""
    
    def __init__(self, name, position, team="player", stats=None, character_class="damage"):
        super().__init__(name, position, team, stats)
        
        self.character_class = character_class
        
        # Configurar acciones base
        self.setup_base_actions()
    
    def setup_base_actions(self):
        """Configura SOLO movimiento - el ataque básico viene de AbilityFactory"""
        self.add_action("move", MoveAction())
        # 🎯 ELIMINADO: BasicAttackAction - ahora viene de la configuración
    
    def basic_attack(self, target):
        """🎯 CORREGIDO: Usa la habilidad 'basic_attack' configurada por AbilityFactory"""
        if "basic_attack" in self.actions:
            from game.systems.action_system.base_action import ActionContext
            context = ActionContext(caster=self, target=target, entities=[])
            return self.actions["basic_attack"].execute(context)
        else:
            # Fallback por si no tiene habilidad básica configurada
            damage = max(1, self.stats['attack'] - target.stats['defense'] // 2)
            target.stats['current_hp'] -= damage
            self.has_acted = True
            print(f"⚔️ {self.name} atacó a {target.name} por {damage} daño!")
            return True