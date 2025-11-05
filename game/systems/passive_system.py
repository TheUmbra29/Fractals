from game.core.event_system import event_system, EventTypes

class PassiveSystem:
    """Sistema para gestionar pasivas de todos los personajes de forma modular"""
    
    def __init__(self):
        self.registered_passives = {}  # entity_id -> list of passive functions
    
    def register_passive(self, entity, passive_name, event_type, callback):
        """Registra una pasiva para una entidad"""
        entity_id = id(entity)
        
        if entity_id not in self.registered_passives:
            self.registered_passives[entity_id] = []
        
        # Registrar el callback para el evento específico
        event_system.subscribe(event_type, callback)
        
        self.registered_passives[entity_id].append({
            'name': passive_name,
            'event_type': event_type,
            'callback': callback
        })
        
        print(f"🔔 Pasiva registrada: {passive_name} para {entity.name}")
    
    def unregister_passives(self, entity):
        """Remueve todas las pasivas de una entidad"""
        entity_id = id(entity)
        
        if entity_id in self.registered_passives:
            for passive in self.registered_passives[entity_id]:
                event_system.unsubscribe(passive['event_type'], passive['callback'])
            
            del self.registered_passives[entity_id]
            print(f"🔕 Todas las pasivas removidas de {entity.name}")
    
    def get_entity_passives(self, entity):
        """Obtiene todas las pasivas de una entidad"""
        entity_id = id(entity)
        return self.registered_passives.get(entity_id, [])

# Fábrica de pasivas predefinidas
class PassiveFactory:
    """Factory para crear pasivas comunes sin duplicar código"""
    
    @staticmethod
    def create_ph_regen_on_kill(entity, ph_amount=50, passive_name="Instinto del Vacío"):
        """Crea una pasiva que regenera PH al matar enemigos"""
        def on_entity_died(data):
            killer = data.get('killer')
            if killer == entity:
                old_ph = entity.stats['current_ph']
                entity.stats['current_ph'] = min(entity.stats['max_ph'], old_ph + ph_amount)
                
                print(f"🎯 {passive_name}: {entity.name} regenera {ph_amount} PH!")
                
                event_system.emit(EventTypes.PH_CHANGED, {
                    'entity': entity,
                    'old_ph': old_ph,
                    'new_ph': entity.stats['current_ph'],
                    'change': ph_amount,
                    'reason': passive_name
                })
        
        return passive_name, EventTypes.ENTITY_DIED, on_entity_died
    
    @staticmethod
    def create_ph_regen_on_ally_attack(entity, ph_amount=10, ult_charge_percent=4, passive_name="Corazón Tempestuoso"):
        """Crea una pasiva que regenera PH cuando aliados atacan"""
        def on_ability_used(data):
            caster = data.get('caster')
            if (caster and caster != entity and caster.team == entity.team and 
                data.get('ability') != 'move'):  # Excluir movimiento
                
                old_ph = entity.stats['current_ph']
                entity.stats['current_ph'] = min(entity.stats['max_ph'], old_ph + ph_amount)
                
                print(f"💙 {passive_name}: {entity.name} recupera {ph_amount} PH por {caster.name}")
                
                event_system.emit(EventTypes.PH_CHANGED, {
                    'entity': entity,
                    'old_ph': old_ph,
                    'new_ph': entity.stats['current_ph'],
                    'change': ph_amount,
                    'reason': passive_name
                })
                
                # Aquí podríamos agregar la recarga de ultimate después
                # Por ahora solo el PH
        
        return passive_name, EventTypes.ABILITY_USED, on_ability_used
    
    @staticmethod
    def create_movement_buff(entity, evasion_bonus=0.8, dash_damage_multiplier=1.0, passive_name="Red Aura"):
        """Crea una pasiva que da beneficios durante el movimiento"""
        def on_entity_moved(data):
            moved_entity = data.get('entity')
            if moved_entity == entity:
                # Aquí aplicamos los beneficios de Red Aura
                # Por ahora solo un mensaje, luego implementaremos los efectos reales
                print(f"🔴 {passive_name} activa: {entity.name} obtiene bonuses de movimiento")
                
                # En el futuro: aplicar efecto de evasión y aumento de daño de embestida
                # self.effect_system.add_effect(entity, some_effect)
        
        return passive_name, EventTypes.ENTITY_MOVED, on_entity_moved