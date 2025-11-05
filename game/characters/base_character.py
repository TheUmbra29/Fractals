from game.entities.character import Character
from game.systems.ability_factory import AbilityFactory
from game.core.event_system import event_system, EventTypes

class BaseCharacter(Character):
    def __init__(self, name, position, team, stats, role, abilities_config):
        super().__init__(name, position, team, stats, role)
        self.abilities_config = abilities_config
        self.passives = []
        self.pending_post_action_move = False
        self.post_action_move_range = 0
        self.base_movement = 3
        
        # 🎯 SISTEMA DE ENERGÍA FLEXIBLE
        self.energy_stats = {
            'current_energy': 0,
            'max_energy': stats.get('max_energy', 100),
            'energy_sources': self.setup_energy_sources(),
            'energy_gain_multipliers': self.setup_energy_multipliers()
        }
        
        self.setup_unique_abilities()
        self.setup_passives()
        self.setup_energy_listeners()
    
    @property
    def movement_range(self):
        speed_bonus = max(0, (self.stats.get('speed', 5) - 5) // 2)
        return self.base_movement + speed_bonus
    
    def setup_unique_abilities(self):
        for ability_key, ability_config in self.abilities_config.items():
            ability_config_with_key = ability_config.copy()
            ability_config_with_key['key'] = ability_key
            ability_instance = AbilityFactory.create_ability(ability_config_with_key)
            self.actions[ability_key] = ability_instance
        
        print(f"🎭 {self.name} - Habilidades cargadas: {list(self.actions.keys())}")
    
    def setup_passives(self):
        pass
    
    def add_passive(self, passive_name, event_type, callback):
        self.passives.append({
            'name': passive_name,
            'event_type': event_type,
            'callback': callback
        })
    
    def register_passives(self, passive_system):
        for passive in self.passives:
            passive_system.register_passive(
                self, 
                passive['name'], 
                passive['event_type'], 
                passive['callback']
            )
    
    # 🎯 SISTEMA DE ENERGÍA
    def setup_energy_sources(self):
        """Fuentes base de energía - SOBREESCRIBIBLE por personaje"""
        return {
            'on_hit': {'base': 8, 'type': 'flat'},
            'on_take_damage': {'base': 5, 'type': 'flat'},  
            'on_ability_use': {'base': 10, 'type': 'flat'},
            'on_kill': {'base': 25, 'type': 'flat'},
            'on_heal': {'base': 5, 'type': 'flat'},
            'on_buff': {'base': 8, 'type': 'flat'},
            'per_turn': {'base': 5, 'type': 'flat'}
        }
    
    def setup_energy_multipliers(self):
        """Multiplicadores base - SOBREESCRIBIBLE por personaje"""
        return {
            'physical_damage': 1.0,
            'energy_damage': 1.2,
            'void_damage': 1.5,
            'light_damage': 1.3,
            'storm_damage': 1.4,
            'ultimate_ability': 0.0
        }
    
    def setup_energy_listeners(self):
        """Registra listeners para ganar energía"""
        from game.core.event_system import event_system, EventTypes
        
        # Ganar energía al golpear (con multiplicador por tipo de daño)
        def on_deal_damage(data):
            if data.get('attacker') == self:
                damage_type = data.get('damage_type', 'physical')
                multiplier = self.energy_stats['energy_gain_multipliers'].get(damage_type, 1.0)
                base_energy = self.energy_stats['energy_sources']['on_hit']['base']
                energy_gain = int(base_energy * multiplier)
                self.gain_energy(energy_gain, f"golpear_{damage_type}")
        
        # Ganar energía al recibir daño
        def on_take_damage(data):
            if data.get('target') == self:
                base_energy = self.energy_stats['energy_sources']['on_take_damage']['base']
                self.gain_energy(base_energy, "recibir_daño")
        
        # Ganar energía al usar habilidad (pero no ultimate)
        def on_ability_used(data):
            if data.get('caster') == self and not data.get('is_ultimate', False):
                base_energy = self.energy_stats['energy_sources']['on_ability_use']['base']
                self.gain_energy(base_energy, "usar_habilidad")
        
        # Ganar energía por eliminación
        def on_entity_killed(data):
            if data.get('killer') == self:
                base_energy = self.energy_stats['energy_sources']['on_kill']['base']
                self.gain_energy(base_energy, "eliminación")
        
        # Ganar energía por aplicar buff
        def on_buff_applied(data):
            if data.get('source') == self:
                base_energy = self.energy_stats['energy_sources']['on_buff']['base']
                self.gain_energy(base_energy, "aplicar_buff")
        
        # Ganar energía por turno
        def on_turn_start(data):
            if data.get('entity') == self:
                base_energy = self.energy_stats['energy_sources']['per_turn']['base']
                self.gain_energy(base_energy, "inicio_turno")
        
        event_system.register(EventTypes.ENTITY_DAMAGED, on_deal_damage)
        event_system.register(EventTypes.ENTITY_DAMAGED, on_take_damage)
        event_system.register(EventTypes.ABILITY_USED, on_ability_used)
        event_system.register(EventTypes.ENTITY_KILLED, on_entity_killed)
        event_system.register(EventTypes.EFFECT_APPLIED, on_buff_applied)
        event_system.register(EventTypes.TURN_STARTED, on_turn_start)
    
    def gain_energy(self, amount, source="unknown"):
        """Aumenta energía con límite máximo"""
        old_energy = self.energy_stats['current_energy']
        
        # Aplicar modificadores
        modified_amount = self.apply_energy_modifiers(amount, source)
        
        new_energy = min(self.energy_stats['max_energy'], old_energy + modified_amount)
        self.energy_stats['current_energy'] = new_energy
        
        actual_gain = new_energy - old_energy
        
        if actual_gain > 0:
            print(f"⚡ {self.name} +{actual_gain} energía ({source}) - Total: {new_energy}/{self.energy_stats['max_energy']}")
        
        # Emitir evento para UI
        from game.core.event_system import event_system, EventTypes
        event_system.emit(EventTypes.ENERGY_CHANGED, {
            'entity': self,
            'old_energy': old_energy,
            'new_energy': new_energy,
            'change_amount': actual_gain,
            'source': source
        })
    
    def apply_energy_modifiers(self, base_amount, source):
        """Aplica modificadores a la energía ganada"""
        return base_amount
    
    def can_use_ultimate(self, ability_config):
        """Verifica si puede usar una habilidad definitiva específica"""
        energy_cost = ability_config.get('energy_cost', 100)
        return self.energy_stats['current_energy'] >= energy_cost
    
    def consume_ultimate_energy(self, energy_cost):
        """Consume energía para ultimate - maneja costos variables"""
        if self.energy_stats['current_energy'] >= energy_cost:
            self.energy_stats['current_energy'] -= energy_cost
            print(f"💥 {self.name} consumió {energy_cost} de energía para ultimate!")
            return True
        return False
    
    def get_energy_percentage(self):
        """Devuelve porcentaje de energía actual"""
        return (self.energy_stats['current_energy'] / self.energy_stats['max_energy']) * 100
    
    def get_energy_absolute(self):
        """Devuelve energía actual en puntos absolutos"""
        return self.energy_stats['current_energy']
    
    def get_character_info(self):
        info = {
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
        info['passives'] = [passive['name'] for passive in self.passives]
        return info

    def reset_turn(self):
        self.has_moved = False
        self.has_acted = False
        self.pending_post_action_move = False
        self.post_action_move_range = 0
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])