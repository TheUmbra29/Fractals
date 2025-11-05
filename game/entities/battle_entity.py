# game/entities/battle_entity.py
"""
Entidad de batalla unificada - combina GameEntity + BaseCharacter
Diseñada para ser la única clase de entidad en batalla
"""

from .game_entity import GameEntity
from game.systems.ability_factory import AbilityFactory
from game.core.event_system import event_system, EventTypes

class BattleEntity(GameEntity):
    """
    Entidad completa para batallas - incluye sistema de energía, habilidades y pasivas
    Reemplaza tanto Character como BaseCharacter
    """
    
    def __init__(self, name, position, team="player", stats=None, 
                 character_class="damage", abilities_config=None):
        # Inicializar GameEntity con stats extendidas
        extended_stats = stats or {}
        if 'max_energy' not in extended_stats:
            extended_stats['max_energy'] = 100
            
        super().__init__(name, position, team, extended_stats)
        
        self.character_class = character_class
        self.abilities_config = abilities_config or {}
        self.passives = []
        self.pending_post_action_move = False
        self.post_action_move_range = 0
        self.base_movement = 3
        
        # 🎯 SISTEMA DE ENERGÍA (de BaseCharacter)
        self.energy_stats = {
            'current_energy': 0,
            'max_energy': self.stats.get('max_energy', 100),
            'energy_sources': self.setup_energy_sources(),
            'energy_gain_multipliers': self.setup_energy_multipliers()
        }
        
        # Configurar habilidades y pasivas
        self.setup_abilities()
        self.setup_energy_listeners()
    
    @property
    def movement_range(self):
        """Rango de movimiento calculado desde velocidad"""
        speed_bonus = max(0, (self.stats.get('speed', 5) - 5) // 2)
        return self.base_movement + speed_bonus
    
    def setup_abilities(self):
        """Configura habilidades desde la configuración"""
        for ability_key, ability_config in self.abilities_config.items():
            ability_config_with_key = ability_config.copy()
            ability_config_with_key['key'] = ability_key
            ability_instance = AbilityFactory.create_ability(ability_config_with_key)
            self.actions[ability_key] = ability_instance
        
        print(f"🎭 {self.name} - Habilidades: {list(self.actions.keys())}")
    
    # 🎯 MÉTODOS DE ENERGÍA (de BaseCharacter)
    def setup_energy_sources(self):
        return {
            'on_hit': {'base': 8, 'type': 'flat'},
            'on_take_damage': {'base': 5, 'type': 'flat'},  
            'on_ability_use': {'base': 10, 'type': 'flat'},
            'on_kill': {'base': 25, 'type': 'flat'},
            'per_turn': {'base': 5, 'type': 'flat'}
        }
    
    def setup_energy_multipliers(self):
        return {
            'physical_damage': 1.0,
            'energy_damage': 1.2,
            'void_damage': 1.5,
            'light_damage': 1.3,
        }
    
    def setup_energy_listeners(self):
        """Listeners para ganar energía"""
        def on_deal_damage(data):
            if data.get('attacker') == self:
                damage_type = data.get('damage_type', 'physical')
                multiplier = self.energy_stats['energy_gain_multipliers'].get(damage_type, 1.0)
                base_energy = self.energy_stats['energy_sources']['on_hit']['base']
                energy_gain = int(base_energy * multiplier)
                self.gain_energy(energy_gain, f"golpear_{damage_type}")
        
        def on_take_damage(data):
            if data.get('target') == self:
                base_energy = self.energy_stats['energy_sources']['on_take_damage']['base']
                self.gain_energy(base_energy, "recibir_daño")
        
        def on_ability_used(data):
            if data.get('caster') == self and not data.get('is_ultimate', False):
                base_energy = self.energy_stats['energy_sources']['on_ability_use']['base']
                self.gain_energy(base_energy, "usar_habilidad")
        
        def on_turn_start(data):
            if data.get('entity') == self:
                base_energy = self.energy_stats['energy_sources']['per_turn']['base']
                self.gain_energy(base_energy, "inicio_turno")
        
        event_system.register(EventTypes.ENTITY_DAMAGED, on_deal_damage)
        event_system.register(EventTypes.ENTITY_DAMAGED, on_take_damage)
        event_system.register(EventTypes.ABILITY_USED, on_ability_used)
        event_system.register(EventTypes.TURN_STARTED, on_turn_start)
    
    def gain_energy(self, amount, source="unknown"):
        old_energy = self.energy_stats['current_energy']
        new_energy = min(self.energy_stats['max_energy'], old_energy + amount)
        self.energy_stats['current_energy'] = new_energy
        
        actual_gain = new_energy - old_energy
        if actual_gain > 0:
            print(f"⚡ {self.name} +{actual_gain} energía ({source})")
            
            # Emitir evento para UI
            event_system.emit(EventTypes.ENERGY_CHANGED, {
                'entity': self,
                'old_energy': old_energy,
                'new_energy': new_energy,
                'change_amount': actual_gain,
                'source': source
            })
    
    def can_use_ultimate(self, ability_config):
        energy_cost = ability_config.get('energy_cost', 100)
        return self.energy_stats['current_energy'] >= energy_cost
    
    def consume_ultimate_energy(self, energy_cost):
        if self.energy_stats['current_energy'] >= energy_cost:
            self.energy_stats['current_energy'] -= energy_cost
            print(f"💥 {self.name} consumió {energy_cost} de energía!")
            return True
        return False
    
    def get_energy_percentage(self):
        return (self.energy_stats['current_energy'] / self.energy_stats['max_energy']) * 100
    
    def get_energy_absolute(self):
        return self.energy_stats['current_energy']
    
    def reset_turn(self):
        """Reset completo del turno"""
        self.has_moved = False
        self.has_acted = False
        self.pending_post_action_move = False
        self.post_action_move_range = 0
    
    # 🎯 COMPATIBILIDAD CON CÓDIGO EXISTENTE
    def basic_attack(self, target):
        """Ataque básico usando el sistema de habilidades"""
        if "basic_attack" in self.actions:
            from game.core.action_base import ActionContext
            context = ActionContext(caster=self, target=target, entities=[])
            return self.actions["basic_attack"].execute(context)
        else:
            # Fallback
            damage = max(1, self.stats['attack'] - target.stats['defense'] // 2)
            target.stats['current_hp'] -= damage
            self.has_acted = True
            print(f"⚔️ {self.name} atacó a {target.name} por {damage} daño!")
            return True
    
    def get_character_info(self):
        """Información del personaje para UI"""
        return {
            'name': self.name,
            'role': self.character_class,
            'hp': f"{self.stats['current_hp']}/{self.stats['max_hp']}",
            'ph': f"{self.stats['current_ph']}/{self.stats['max_ph']}",
            'energy': f"{self.get_energy_absolute()}/{self.energy_stats['max_energy']}",
            'attack': self.stats['attack'],
            'defense': self.stats['defense'],
            'speed': self.stats['speed'],
            'movement_range': self.movement_range,
            'abilities': list(self.actions.keys())
        }