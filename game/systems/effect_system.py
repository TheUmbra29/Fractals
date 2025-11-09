"""
Sistema de efectos - VERSIÓN CORREGIDA SIN IMPORTACIONES CIRCULARES
"""
from typing import Dict, List, Any
from game.core.logger import logger

class GenericEffect:
    """Efecto genérico que se configura completamente por datos"""
    
    def __init__(self, effect_data: Dict[str, Any], source):
        self.effect_id = effect_data['id']
        self.name = effect_data['name']
        self.duration = effect_data.get('duration', 1)
        self.effect_type = effect_data.get('type', 'neutral')
        self.source = source
        self.config = effect_data
        self.stacks = 1
        self.current_turn = 0
        self.is_active = True
        
        # Estado interno para efectos complejos
        self._state = {}
    
    def on_apply(self, target):
        logger.info(f"{target.name} recibe {self.name}")
        self._execute_actions('on_apply', target)
        from game.core.event_system import event_system, EventTypes
        event_system.emit(EventTypes.EFFECT_APPLIED, {
            'target': target, 'effect': self, 'source': self.source
        })
    
    def on_turn_start(self, target):
        self.current_turn += 1
        self._execute_actions('on_turn_start', target)
    
    def on_turn_end(self, target):
        self._execute_actions('on_turn_end', target)
    
    def on_damage_taken(self, target, damage_data):
        self._execute_actions('on_damage_taken', target, damage_data)
    
    def on_remove(self, target):
        self._execute_actions('on_remove', target)
        logger.debug(f"{target.name} pierde {self.name}")
        from game.core.event_system import event_system, EventTypes
        event_system.emit(EventTypes.EFFECT_REMOVED, {
            'target': target, 'effect': self, 'source': self.source
        })
    
    def _execute_actions(self, trigger: str, target, extra_data=None):
        """Ejecuta todas las acciones para un trigger dado"""
        actions = self.config.get('actions', {}).get(trigger, [])
        
        for action in actions:
            self._execute_action(action, target, extra_data)
    
    def _execute_action(self, action: Dict[str, Any], target, extra_data=None):
        """Ejecuta una acción individual"""
        action_type = action['type']
        
        if action_type == 'damage':
            self._action_damage(action, target)
        elif action_type == 'heal':
            self._action_heal(action, target)
        elif action_type == 'modify_stat':
            self._action_modify_stat(action, target)
        elif action_type == 'modify_damage':
            self._action_modify_damage(action, target, extra_data)
        elif action_type == 'custom':
            self._action_custom(action, target, extra_data)
    
    def _action_damage(self, action, target):
        """Acción: aplicar daño SIMPLIFICADO - sin tipos de daño"""
        base_damage = action.get('value', 0)
        
        # Calcular daño final
        damage = self._calculate_value(base_damage, action.get('calculation'), target)
        damage *= self.stacks
        
        if damage > 0:
            target.stats['current_hp'] -= damage
            logger.combat_event(f"Efecto {self.name}", self.source, target, damage=damage)
            
            from game.core.event_system import event_system, EventTypes
            event_system.emit(EventTypes.ENTITY_DAMAGED, {
                'attacker': self.source,
                'target': target,
                'damage': damage,
                'source_effect': self.name
            })
    
    def _action_heal(self, action, target):
        """Acción: curar"""
        heal_amount = action.get('value', 0)
        heal_amount = self._calculate_value(heal_amount, action.get('calculation'), target)
        heal_amount *= self.stacks
        
        if heal_amount > 0:
            old_hp = target.stats['current_hp']
            target.stats['current_hp'] = min(
                target.stats['max_hp'], 
                old_hp + heal_amount
            )
            actual_heal = target.stats['current_hp'] - old_hp
            
            logger.combat_event(f"Efecto {self.name}", self.source, target, healing=actual_heal)
            
            from game.core.event_system import event_system, EventTypes
            event_system.emit(EventTypes.ENTITY_HEALED, {
                'healer': self.source,
                'target': target,
                'amount': actual_heal,
                'source_effect': self.name
            })
    
    def _action_modify_stat(self, action, target):
        """Acción: modificar estadística"""
        stat = action['stat']
        modifier = action['value']
        operation = action.get('operation', 'add')  # add, multiply, set
        
        # Guardar valor original si es la primera vez
        if f'original_{stat}' not in self._state:
            self._state[f'original_{stat}'] = target.stats.get(stat, 0)
        
        current_value = target.stats.get(stat, 0)
        original_value = self._state[f'original_{stat}']
        
        if operation == 'add':
            target.stats[stat] = original_value + (modifier * self.stacks)
        elif operation == 'multiply':
            target.stats[stat] = int(original_value * (1 + modifier))
        elif operation == 'set':
            target.stats[stat] = modifier
        
        logger.debug(f"{target.name} {stat}: {original_value} → {target.stats[stat]}")
    
    def _action_modify_damage(self, action, target, damage_data):
        """Acción: modificar daño entrante/saliente"""
        if not damage_data:
            return
            
        modifier_type = action.get('modifier_type', 'incoming')  # incoming, outgoing
        value = action.get('value', 0)
        operation = action.get('operation', 'reduce')  # reduce, increase, set
        
        if modifier_type == 'incoming':
            if operation == 'reduce':
                damage_data['damage'] = max(0, damage_data['damage'] - value)
            elif operation == 'reduce_percent':
                reduction = int(damage_data['damage'] * value)
                damage_data['damage'] -= reduction
                logger.debug(f"{self.name} redujo {reduction} daño")
    
    def _action_custom(self, action, target, extra_data):
        """Acción: lógica personalizada - VERSIÓN MEJORADA"""
        callback_name = action.get('callback')
        if callback_name:
            logger.debug(f"Ejecutando callback personalizado: {callback_name}")
            return self._execute_custom_callback(callback_name, target, extra_data)
        return False
    
    def _execute_custom_callback(self, callback_name, target, extra_data):
        """Ejecuta callbacks usando duck typing en lugar de imports específicos"""
        try:
            if callback_name == "enable_improved_dash":
                return self._callback_enable_improved_dash(target)
            elif callback_name == "recharge_ultimate":
                return self._callback_recharge_ultimate(target)
            elif callback_name == "apply_hyper_speed":
                return self._callback_hyper_speed(target)
            else:
                logger.warning(f"Callback desconocido: {callback_name}")
                return False
        except Exception as e:
            logger.error(f"Error en callback {callback_name}", exception=e)
            return False
    
    def _callback_enable_improved_dash(self, target):
        """Usa hasattr en lugar de asumir el tipo específico"""
        if hasattr(target, 'pending_post_action_move'):
            target.pending_post_action_move = True
            target.post_action_move_range = 3
            logger.info(f"⚡ {target.name} obtiene embestida mejorada!")
            return True
        return False
    
    def _callback_recharge_ultimate(self, target):
        """Verifica la existencia de energy_stats dinámicamente"""
        if hasattr(target, 'energy_stats'):
            target.energy_stats['current_energy'] = target.energy_stats['max_energy']
            logger.info(f"✨ {target.name} recarga energía ultimate al máximo!")
            return True
        return False
    
    def _callback_hyper_speed(self, target):
        """Accede a stats de forma genérica"""
        if hasattr(target, 'stats') and 'speed' in target.stats:
            original_speed = target.stats.get('speed', 10)
            target.stats['speed'] = original_speed + 50
            logger.info(f"🌀 {target.name} obtiene hipervelocidad! (+50 velocidad)")
            return True
        return False
    
    def _calculate_value(self, base_value, calculation_config, target):
        """Calcula valores basado en fórmulas"""
        if not calculation_config:
            return base_value
        
        formula = calculation_config.get('formula', 'static')
        
        if formula == 'scales_with_source_stat':
            stat = calculation_config.get('stat', 'attack')
            multiplier = calculation_config.get('multiplier', 1.0)
            return int(base_value * self.source.stats.get(stat, 1) * multiplier)
        
        elif formula == 'percentage_of_target_max':
            stat = calculation_config.get('stat', 'max_hp')
            return int(base_value * target.stats.get(stat, 100) / 100)
        
        elif formula == 'percentage_of_source_stat':
            stat = calculation_config.get('stat', 'attack') 
            return int(base_value * self.source.stats.get(stat, 1))
        
        elif formula == 'scales_with_turn':
            multiplier = calculation_config.get('multiplier', 1.0)
            return int(base_value * self.current_turn * multiplier)
        
        return base_value
    
    def is_expired(self):
        return self.current_turn >= self.duration
    
    def can_stack(self, new_effect):
        return self.effect_id == new_effect.effect_id
    
    def add_stack(self, amount=1):
        self.stacks += amount
        self.current_turn = 0


class EffectSystem:
    """Sistema para manejar efectos persistentes - VERSIÓN MEJORADA"""
    
    def __init__(self, game_context=None):
        self.game_context = game_context
        self.entity_effects: Dict[str, List[GenericEffect]] = {}
        self.effects_registry = {}
        logger.debug("EffectSystem inicializado")
    
    def load_effects_config(self, effects_config: Dict):
        """Carga la configuración de efectos"""
        self.effects_registry = effects_config
        logger.info(f"EffectSystem cargó {len(effects_config)} efectos")
    
    def apply_effect(self, target, effect_id: str, source):
        """Aplica un efecto por su ID - VERSIÓN COMPLETA"""
        if effect_id not in self.effects_registry:
            logger.error(f"Efecto no encontrado: {effect_id}")
            return False
        
        try:
            effect_config = self.effects_registry[effect_id]
            effect = GenericEffect(effect_config, source)
            
            if target not in self.entity_effects:
                self.entity_effects[target] = []
            
            # Stacking - verificar si ya existe el efecto
            existing_effect = next(
                (e for e in self.entity_effects[target] 
                 if e.effect_id == effect_id), None
            )
            
            if existing_effect and existing_effect.can_stack(effect):
                existing_effect.add_stack()
                logger.info(f"📚 {effect.name} stackeado a {existing_effect.stacks} en {target.name}")
                return True
            else:
                self.entity_effects[target].append(effect)
                effect.on_apply(target)
                return True
                
        except Exception as e:
            logger.error(f"Error aplicando efecto {effect_id} a {target.name}", exception=e)
            return False
    
    def update_effects(self, entities):
        """Actualiza todos los efectos al final del turno - MEJORADO"""
        effects_to_remove = []
        
        for entity in entities:
            if entity not in self.entity_effects:
                continue
                
            for effect in self.entity_effects[entity]:
                effect.on_turn_end(entity)
                
                if effect.is_expired():
                    effect.on_remove(entity)
                    effects_to_remove.append((entity, effect))
                    logger.debug(f"⌛ {effect.name} expiró en {entity.name}")
                elif not effect.is_active:
                    effect.on_remove(entity)
                    effects_to_remove.append((entity, effect))
                    logger.debug(f"🚫 {effect.name} desactivado en {entity.name}")
        
        # Remover efectos expirados
        for entity, effect in effects_to_remove:
            if entity in self.entity_effects:
                self.entity_effects[entity].remove(effect)
        
        if effects_to_remove:
            logger.info(f"🔄 EffectSystem actualizado: {len(effects_to_remove)} efectos removidos")
    
    def on_turn_start(self, entity):
        """Llamar al inicio del turno de una entidad - MEJORADO"""
        if entity in self.entity_effects:
            for effect in self.entity_effects[entity]:
                effect.on_turn_start(entity)
            
            active_effects = len(self.entity_effects[entity])
            if active_effects > 0:
                logger.debug(f"🔄 {entity.name} tiene {active_effects} efectos activos al inicio del turno")
    
    def on_damage_taken(self, target, damage_data):
        """Notificar a efectos sobre daño entrante - MEJORADO"""
        if target in self.entity_effects:
            effects_triggered = 0
            for effect in self.entity_effects[target]:
                if hasattr(effect, 'on_damage_taken'):
                    effect.on_damage_taken(target, damage_data)
                    effects_triggered += 1
            
            if effects_triggered > 0:
                logger.debug(f"💥 {effects_triggered} efectos activados por daño en {target.name}")
    
    def get_entity_effects(self, entity):
        """Obtiene efectos activos de una entidad"""
        return self.entity_effects.get(entity, [])
    
    def has_effect(self, entity, effect_id):
        """Verifica si una entidad tiene un efecto específico"""
        if entity not in self.entity_effects:
            return False
        return any(e.effect_id == effect_id for e in self.entity_effects[entity])
    
    def remove_effect(self, entity, effect_id):
        """Remueve un efecto específico de una entidad - MEJORADO"""
        if entity in self.entity_effects:
            for effect in self.entity_effects[entity][:]:
                if effect.effect_id == effect_id:
                    effect.on_remove(entity)
                    self.entity_effects[entity].remove(effect)
                    logger.info(f"🧹 {effect.name} removido de {entity.name}")
                    return True
        return False
    
    def get_effect_stats(self):
        """Obtiene estadísticas del sistema de efectos"""
        total_effects = sum(len(effects) for effects in self.entity_effects.values())
        affected_entities = len(self.entity_effects)
        return {
            "total_effects_active": total_effects,
            "entities_affected": affected_entities,
            "effects_loaded": len(self.effects_registry)
        }