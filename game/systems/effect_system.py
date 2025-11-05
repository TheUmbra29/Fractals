from enum import Enum
from game.core.event_system import event_system, EventTypes

class EffectType(Enum):
    BUFF = "buff"
    DEBUFF = "debuff" 
    HEAL_OVER_TIME = "hot"
    DAMAGE_OVER_TIME = "dot"
    CROWD_CONTROL = "cc"
    STAT_MODIFIER = "stat_mod"
    SPECIAL = "special"

class Effect:
    """Clase base para todos los efectos (buffs/debuffs)"""
    
    def __init__(self, name, duration, effect_type, source, **kwargs):
        self.name = name
        self.duration = duration
        self.remaining_duration = duration
        self.effect_type = effect_type
        self.source = source  # Quién aplicó el efecto
        self.stacks = kwargs.get('stacks', 1)
        self.max_stacks = kwargs.get('max_stacks', 1)
        self.is_expired = False
        
        # Modificadores de stats
        self.stat_modifiers = kwargs.get('stat_modifiers', {})
        
        # Callbacks para eventos
        self.on_apply_callback = kwargs.get('on_apply')
        self.on_remove_callback = kwargs.get('on_remove') 
        self.on_tick_callback = kwargs.get('on_tick')
    
    def apply(self, target):
        """Aplica el efecto al objetivo"""
        print(f"🎯 Aplicando {self.name} a {target.name} (duración: {self.duration})")
        
        # Aplicar modificadores de stats
        for stat, value in self.stat_modifiers.items():
            target.stats[stat] += value
        
        # Ejecutar callback de aplicación
        if self.on_apply_callback:
            self.on_apply_callback(self, target)
        
        event_system.emit(EventTypes.EFFECT_APPLIED, {
            'effect': self,
            'target': target,
            'source': self.source
        })
    
    def remove(self, target):
        """Remueve el efecto del objetivo"""
        print(f"🗑️ Removiendo {self.name} de {target.name}")
        
        # Revertir modificadores de stats
        for stat, value in self.stat_modifiers.items():
            target.stats[stat] -= value
        
        # Ejecutar callback de remoción
        if self.on_remove_callback:
            self.on_remove_callback(self, target)
        
        event_system.emit(EventTypes.EFFECT_REMOVED, {
            'effect': self,
            'target': target,
            'source': self.source
        })
    
    def tick(self, target):
        """Ejecuta un tick del efecto (cada turno)"""
        self.remaining_duration -= 1
        
        # Ejecutar callback de tick
        if self.on_tick_callback:
            self.on_tick_callback(self, target)
        
        # Verificar si expiró
        if self.remaining_duration <= 0:
            self.is_expired = True
            event_system.emit(EventTypes.EFFECT_EXPIRED, {
                'effect': self,
                'target': target,
                'source': self.source
            })
        
        return self.is_expired
    
    def refresh(self, new_duration=None):
        """Refresca la duración del efecto"""
        if new_duration:
            self.duration = new_duration
        self.remaining_duration = self.duration
        self.is_expired = False
    
    def add_stack(self):
        """Añade un stack si es apilable"""
        if self.stacks < self.max_stacks:
            self.stacks += 1
            self.refresh()

class EffectSystem:
    """Sistema principal para manejar efectos en el juego"""
    
    def __init__(self):
        self.entity_effects = {}  # entity_id -> list[Effect]
    
    def add_effect(self, entity, effect):
        """Añade un efecto a una entidad"""
        entity_id = id(entity)
        
        if entity_id not in self.entity_effects:
            self.entity_effects[entity_id] = []
        
        # Verificar si el efecto ya existe
        existing_effect = None
        for existing in self.entity_effects[entity_id]:
            if existing.name == effect.name and existing.source == effect.source:
                existing_effect = existing
                break
        
        if existing_effect:
            # Si existe, refrescar o añadir stack
            if existing_effect.max_stacks > 1:
                existing_effect.add_stack()
            else:
                existing_effect.refresh(effect.duration)
            print(f"🔄 Efecto {effect.name} refrescado en {entity.name}")
        else:
            # Si no existe, añadir nuevo efecto
            self.entity_effects[entity_id].append(effect)
            effect.apply(entity)
    
    def remove_effect(self, entity, effect_name, source=None):
        """Remueve un efecto específico de una entidad"""
        entity_id = id(entity)
        
        if entity_id in self.entity_effects:
            effects_to_remove = []
            for effect in self.entity_effects[entity_id]:
                if effect.name == effect_name and (source is None or effect.source == source):
                    effects_to_remove.append(effect)
            
            for effect in effects_to_remove:
                effect.remove(entity)
                self.entity_effects[entity_id].remove(effect)
    
    def remove_all_effects(self, entity, effect_type=None):
        """Remueve todos los efectos de una entidad"""
        entity_id = id(entity)
        
        if entity_id in self.entity_effects:
            effects_to_remove = []
            for effect in self.entity_effects[entity_id]:
                if effect_type is None or effect.effect_type == effect_type:
                    effects_to_remove.append(effect)
            
            for effect in effects_to_remove:
                effect.remove(entity)
                self.entity_effects[entity_id].remove(effect)
    
    def has_effect(self, entity, effect_name, source=None):
        """Verifica si una entidad tiene un efecto específico"""
        entity_id = id(entity)
        
        if entity_id in self.entity_effects:
            for effect in self.entity_effects[entity_id]:
                if effect.name == effect_name and (source is None or effect.source == source):
                    return True
        return False
    
    def get_effects(self, entity, effect_type=None):
        """Obtiene todos los efectos de una entidad"""
        entity_id = id(entity)
        
        if entity_id in self.entity_effects:
            if effect_type:
                return [effect for effect in self.entity_effects[entity_id] if effect.effect_type == effect_type]
            return self.entity_effects[entity_id].copy()
        return []
    
    def update_effects(self, entities):
        """Actualiza todos los efectos (llamar cada turno)"""
        effects_to_remove = []
        
        for entity_id, effects in self.entity_effects.items():
            # Encontrar la entidad por su ID
            entity = None
            for ent in entities:
                if id(ent) == entity_id:
                    entity = ent
                    break
            
            if entity:
                for effect in effects:
                    if effect.tick(entity):
                        effects_to_remove.append((entity_id, effect))
        
        # Remover efectos expirados
        for entity_id, effect in effects_to_remove:
            # Encontrar la entidad nuevamente
            entity = None
            for ent in entities:
                if id(ent) == entity_id:
                    entity = ent
                    break
            
            if entity:
                effect.remove(entity)
                self.entity_effects[entity_id].remove(effect)

# Efectos predefinidos comunes
class SpeedBuffEffect(Effect):
    """Efecto de aumento de velocidad"""
    
    def __init__(self, source, amount, duration):
        super().__init__(
            name="Buff de Velocidad",
            duration=duration,
            effect_type=EffectType.BUFF,
            source=source,
            stat_modifiers={'speed': amount}
        )

class DamageOverTimeEffect(Effect):
    """Efecto de daño over time"""
    
    def __init__(self, source, damage_per_tick, duration, damage_type="magic"):
        super().__init__(
            name=f"DoT {damage_type}",
            duration=duration,
            effect_type=EffectType.DAMAGE_OVER_TIME,
            source=source
        )
        self.damage_per_tick = damage_per_tick
        self.damage_type = damage_type
    
    def on_tick(self, effect, target):
        """Aplica daño cada tick"""
        damage = self.damage_per_tick
        target.stats['current_hp'] -= damage
        
        event_system.emit(EventTypes.ENTITY_DAMAGED, {
            'attacker': self.source,
            'target': target,
            'damage': damage,
            'damage_type': self.damage_type,
            'ability': f"DoT {self.name}"
        })
        
        print(f"🔥 {target.name} recibe {damage} de daño over time")

class HealOverTimeEffect(Effect):
    """Efecto de curación over time"""
    
    def __init__(self, source, heal_per_tick, duration):
        super().__init__(
            name="Curación over time",
            duration=duration,
            effect_type=EffectType.HEAL_OVER_TIME,
            source=source
        )
        self.heal_per_tick = heal_per_tick
    
    def on_tick(self, effect, target):
        """Aplica curación cada tick"""
        heal_amount = min(self.heal_per_tick, target.stats['max_hp'] - target.stats['current_hp'])
        if heal_amount > 0:
            target.stats['current_hp'] += heal_amount
            
            event_system.emit(EventTypes.ENTITY_HEALED, {
                'healer': self.source,
                'target': target,
                'heal_amount': heal_amount,
                'ability': self.name
            })
            
            print(f"💚 {target.name} recupera {heal_amount} HP")