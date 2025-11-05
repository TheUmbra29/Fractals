from game.core.action_base import BaseAction, ActionContext
from game.core.event_system import event_system, EventTypes

class EffectComponent:
    """Componente base para todos los efectos de habilidades"""
    
    def __init__(self, config):
        self.config = config
    
    def apply(self, context):
        raise NotImplementedError("Los efectos deben implementar apply()")
    
    def validate(self, context):
        return True
    
    def _calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class DamageEffect(EffectComponent):
    """Efecto de daño genérico"""
    
    def apply(self, context):
        multiplier = self.config.get('multiplier', 1.0)
        damage_type = self.config.get('damage_type', 'physical')
        aoe_radius = self.config.get('aoe_radius', 0)
        target_filter = self.config.get('target', 'enemies')
        
        targets = self._get_targets(context, aoe_radius, target_filter)
        total_damage = 0
        
        for i, target in enumerate(targets):
            if isinstance(multiplier, list):
                current_multiplier = multiplier[min(i, len(multiplier) - 1)]
            else:
                current_multiplier = multiplier
                
            damage = max(1, int(
                (context.caster.stats['attack'] - target.stats['defense'] // 2) * current_multiplier
            ))
            
            target.stats['current_hp'] -= damage
            total_damage += damage
            
            event_system.emit(EventTypes.ENTITY_DAMAGED, {
                'attacker': context.caster,
                'target': target,
                'damage': damage,
                'ability': context.ability_name,
                'damage_type': damage_type
            })
            
            print(f"⚔️ {context.caster.name} → {target.name}: {damage} daño")
        
        return len(targets) > 0
    
    def _get_targets(self, context, aoe_radius, target_filter):
        targets = []
        
        if aoe_radius > 0 and context.target_position:
            for entity in context.entities:
                distance = self._calculate_distance(context.target_position, entity.position)
                if distance <= aoe_radius and self._is_valid_target(entity, context.caster, target_filter):
                    targets.append(entity)
        elif context.target and self._is_valid_target(context.target, context.caster, target_filter):
            targets = [context.target]
        elif context.entities:
            targets = [e for e in context.entities if self._is_valid_target(e, context.caster, target_filter)]
        
        return targets
    
    def _is_valid_target(self, target, caster, target_filter):
        if target_filter == 'enemies':
            return target.team != caster.team
        elif target_filter == 'allies':
            return target.team == caster.team
        elif target_filter == 'all':
            return True
        return target.team != caster.team

class HealEffect(EffectComponent):
    """Efecto de curación genérico"""
    
    def apply(self, context):
        amount = self.config.get('amount', 0)
        aoe_radius = self.config.get('aoe_radius', 0)
        target_filter = self.config.get('target', 'allies')
        
        targets = self._get_targets(context, aoe_radius, target_filter)
        total_healing = 0
        
        for target in targets:
            max_possible_heal = target.stats['max_hp'] - target.stats['current_hp']
            heal = min(amount, max_possible_heal)
            
            if heal > 0:
                target.stats['current_hp'] += heal
                total_healing += heal
                
                event_system.emit(EventTypes.ENTITY_HEALED, {
                    'healer': context.caster,
                    'target': target,
                    'amount': heal,
                    'ability': context.ability_name
                })
                
                print(f"💚 {context.caster.name} → {target.name}: +{heal} HP")
        
        print(f"🏥 {context.caster.name} curó {total_healing} HP a {len(targets)} objetivos")
        return len(targets) > 0
    
    def _get_targets(self, context, aoe_radius, target_filter):
        targets = []
        
        if aoe_radius > 0 and context.target_position:
            for entity in context.entities:
                distance = self._calculate_distance(context.target_position, entity.position)
                if distance <= aoe_radius and self._is_valid_target(entity, context.caster, target_filter):
                    targets.append(entity)
        elif context.target and self._is_valid_target(context.target, context.caster, target_filter):
            targets = [context.target]
        elif target_filter == 'allies' and context.entities:
            targets = [e for e in context.entities if e.team == context.caster.team]
        elif target_filter == 'all' and context.entities:
            targets = context.entities
        
        return targets
    
    def _is_valid_target(self, target, caster, target_filter):
        if target_filter == 'allies':
            return target.team == caster.team
        elif target_filter == 'all':
            return True
        return target.team == caster.team

class MovementEffect(EffectComponent):
    """Efecto de movimiento/teletransporte"""
    
    def apply(self, context):
        move_type = self.config.get('move_type', 'teleport')
        range_distance = self.config.get('range', 1)
        
        if move_type == 'teleport' and context.target_position:
            old_pos = context.caster.position
            context.caster.position = context.target_position
            print(f"✨ {context.caster.name} se teletransportó: {old_pos} → {context.target_position}")
            return True
        
        elif move_type == 'line_movement' and context.extra_data:
            direction = context.extra_data.get('direction', (0, 0))
            max_length = context.extra_data.get('line_length', range_distance)
            
            old_pos = context.caster.position
            new_pos = self._calculate_line_end_position(old_pos, direction, max_length)
            
            context.caster.position = new_pos
            print(f"💨 {context.caster.name} se desplaza en línea: {old_pos} → {new_pos}")
            return True
        
        elif move_type == 'post_action':
            context.caster.pending_post_action_move = True
            context.caster.post_action_move_range = range_distance
            print(f"🎯 {context.caster.name} prepara movimiento posterior de {range_distance} casillas")
            return True
        
        return False
    
    def _calculate_line_end_position(self, start_pos, direction, max_length):
        from game.systems.grid_system import GridSystem
        grid_system = GridSystem()
        
        current_pos = start_pos
        
        for i in range(max_length):
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            
            if not grid_system.is_valid_position(next_pos):
                break
            
            current_pos = next_pos
        
        return current_pos

class BuffEffect(EffectComponent):
    """Efecto de mejora de estadísticas"""
    
    def apply(self, context):
        stat_buffs = self.config.get('stat_buffs', {})
        duration = self.config.get('duration', 1)
        target_type = self.config.get('target', 'self')
        aoe_radius = self.config.get('aoe_radius', 0)
        
        if target_type == 'self':
            targets = [context.caster]
        elif target_type == 'selected' and context.target:
            targets = [context.target]
        elif target_type == 'allies' and context.entities:
            targets = [e for e in context.entities if e.team == context.caster.team]
        elif aoe_radius > 0 and context.target_position and context.entities:
            targets = []
            for entity in context.entities:
                distance = self._calculate_distance(context.target_position, entity.position)
                if distance <= aoe_radius and entity.team == context.caster.team:
                    targets.append(entity)
        else:
            targets = [context.caster]
        
        for target in targets:
            print(f"🛡️ {target.name} recibe buff: {stat_buffs} por {duration} turnos")
        
        return len(targets) > 0

class StatusEffect(EffectComponent):
    """Efecto de aplicación de estados"""
    
    def apply(self, context):
        status_type = self.config.get('status_type')
        duration = self.config.get('duration', 1)
        value = self.config.get('value', 0)
        target_filter = self.config.get('target', 'enemies')
        
        targets = self._get_targets(context, target_filter)
        
        for target in targets:
            print(f"⚡ {target.name} recibe {status_type} (valor: {value}) por {duration} turnos")
        
        return len(targets) > 0
    
    def _get_targets(self, context, target_filter):
        if context.target:
            return [context.target] if self._is_valid_target(context.target, context.caster, target_filter) else []
        elif context.entities:
            return [e for e in context.entities if self._is_valid_target(e, context.caster, target_filter)]
        return []
    
    def _is_valid_target(self, target, caster, target_filter):
        if target_filter == 'enemies':
            return target.team != caster.team
        elif target_filter == 'allies':
            return target.team == caster.team
        elif target_filter == 'all':
            return True
        return target.team != caster.team

class ChainMovementEffect(EffectComponent):
    """Efecto de movimiento en cadena"""
    
    def apply(self, context):
        if not context.entities or len(context.entities) == 0:
            print("❌ ChainMovement: No hay objetivos para la cadena")
            return False
        
        caster = context.caster
        targets = context.entities
        multipliers = self.config.get('multiplier', [1.0])
        
        print(f"🎯 Iniciando movimiento en cadena con {len(targets)} objetivos")
        
        total_damage = 0
        for i, target in enumerate(targets):
            current_multiplier = multipliers[min(i, len(multipliers) - 1)]
            damage = self._calculate_damage(caster, target, current_multiplier)
            
            target.stats['current_hp'] -= damage
            total_damage += damage
            
            event_system.emit(EventTypes.ENTITY_DAMAGED, {
                'attacker': caster,
                'target': target,
                'damage': damage,
                'ability': context.ability_name,
                'damage_type': self.config.get('damage_type', 'physical'),
                'chain_position': i + 1
            })
            
            print(f"⛓️ [{i+1}] {caster.name} → {target.name}: {damage} daño")
        
        final_position = self._calculate_final_position(caster, targets)
        
        if final_position and self._is_position_valid(final_position, caster, context.entities):
            old_pos = caster.position
            caster.position = final_position
            print(f"💨 {caster.name} se desplaza: {old_pos} → {final_position}")
        else:
            print("❌ No se pudo calcular posición final válida")
        
        print(f"💥 Cadena completada: {total_damage} daño total")
        return True
    
    def _calculate_damage(self, caster, target, multiplier):
        return max(1, int(
            (caster.stats['attack'] - target.stats['defense'] // 2) * multiplier
        ))
    
    def _calculate_final_position(self, caster, targets):
        if not targets:
            return None
        
        last_target = targets[-1]
        dx = last_target.position[0] - caster.position[0]
        dy = last_target.position[1] - caster.position[1]
        
        if dx != 0: dx = 1 if dx > 0 else -1
        if dy != 0: dy = 1 if dy > 0 else -1
        
        behind_x = last_target.position[0] + dx
        behind_y = last_target.position[1] + dy
        
        return (behind_x, behind_y)
    
    def _is_position_valid(self, position, caster, all_entities):
        from game.systems.grid_system import GridSystem
        grid_system = GridSystem()
        
        if not grid_system.is_valid_position(position):
            return False
        
        for entity in all_entities:
            if entity.position == position and entity != caster:
                return False
        
        return True

class ResourceRecoveryEffect(EffectComponent):
    """Efecto para recuperar PH, energía, etc."""
    
    def apply(self, context):
        ph_recovery = self.config.get('ph_recovery', 0)
        energy_recovery = self.config.get('energy_recovery', 0)
        target_type = self.config.get('target', 'self')
        
        if target_type == 'self':
            targets = [context.caster]
        elif target_type == 'all_allies' and context.entities:
            targets = [e for e in context.entities if e.team == context.caster.team]
        elif target_type == 'selected' and context.target:
            targets = [context.target]
        else:
            targets = [context.caster]
        
        for target in targets:
            if ph_recovery > 0:
                old_ph = target.stats['current_ph']
                target.stats['current_ph'] = min(
                    target.stats['max_ph'],
                    old_ph + ph_recovery
                )
                actual_recovery = target.stats['current_ph'] - old_ph
                if actual_recovery > 0:
                    print(f"🔋 {target.name} recuperó {actual_recovery} PH")
            
            if energy_recovery > 0 and hasattr(target, 'gain_energy'):
                target.gain_energy(energy_recovery, "ability_recovery")
        
        return True

class ApplyEffectComponent(EffectComponent):
    """Componente para aplicar efectos del sistema data-driven"""
    
    def apply(self, context):
        effect_id = self.config.get('effect_id')
        target_type = self.config.get('target', 'enemy')
        
        if not effect_id:
            return False
        
        print(f"⚡ [SISTEMA EFECTOS] {context.caster.name} aplicaría {effect_id} a {target_type}")
        
        # Por ahora solo retornamos True para que la habilidad se ejecute
        # Más adelante conectaremos con el EffectSystem real
        return True

class CleanseEffectsComponent(EffectComponent):
    """Limpia efectos negativos del objetivo"""
    
    def apply(self, context):
        if not context.target:
            return False
        
        print(f"✨ {context.caster.name} limpia efectos de {context.target.name}")
        return True

class UltimateRechargeComponent(EffectComponent):
    """Recarga la ultimate del objetivo"""
    
    def apply(self, context):
        target_type = self.config.get('target', 'self')
        recharge_amount = self.config.get('value', 100)
        
        targets = self._get_targets(context, target_type)
        
        for target in targets:
            if hasattr(target, 'energy_stats'):
                target.energy_stats['current_energy'] = min(
                    target.energy_stats['max_energy'],
                    target.energy_stats['current_energy'] + recharge_amount
                )
                print(f"⚡ {target.name} recibe {recharge_amount} de energía ultimate")
        
        return len(targets) > 0
    
    def _get_targets(self, context, target_type):
        if target_type == 'self':
            return [context.caster]
        elif target_type == 'selected' and context.target:
            return [context.target]
        elif target_type == 'all_allies' and context.entities:
            return [e for e in context.entities if e.team == context.caster.team]
        return []

class ComposableAbility(BaseAction):
    """Habilidad compuesta por múltiples efectos"""
    
    def __init__(self, ability_config):
        name = ability_config['name']
        cost_ph = ability_config.get('cost_ph', 0)
        cooldown = ability_config.get('cooldown', 0)
        range_val = ability_config.get('range', 1)
        selection_mode = ability_config.get('selection_mode', 'enemy')
        
        super().__init__(
            name=name,
            action_type="ability",
            cost_ph=cost_ph,
            cooldown=cooldown,
            selection_mode=selection_mode,
            range=range_val
        )
        
        self.effects_config = ability_config.get('effects', [])
        self.effects = self._build_effects()
        self.ability_config = ability_config
    
    def _build_effects(self):
        effects = []
        for effect_config in self.effects_config:
            effect_type = effect_config['type']
            
            if effect_type == 'damage':
                effects.append(DamageEffect(effect_config))
            elif effect_type == 'heal':
                effects.append(HealEffect(effect_config))
            elif effect_type == 'movement':
                effects.append(MovementEffect(effect_config))
            elif effect_type == 'buff':
                effects.append(BuffEffect(effect_config))
            elif effect_type == 'status':
                effects.append(StatusEffect(effect_config))
            elif effect_type == 'chain_movement':
                effects.append(ChainMovementEffect(effect_config))
            elif effect_type == 'resource_recovery':
                effects.append(ResourceRecoveryEffect(effect_config))
            elif effect_type == 'apply_effect':
                effects.append(ApplyEffectComponent(effect_config))
            elif effect_type == 'cleanse_effects':
                effects.append(CleanseEffectsComponent(effect_config))
            elif effect_type == 'ultimate_recharge':
                effects.append(UltimateRechargeComponent(effect_config))
        
        return effects
    
    def execute(self, context):
        context.ability_name = self.name
        
        success = False
        for effect in self.effects:
            if effect.apply(context):
                success = True
        
        if success:
            context.caster.has_acted = True
            context.caster.stats['current_ph'] -= self.cost_ph
            
            event_system.emit(EventTypes.ABILITY_USED, {
                'caster': context.caster,
                'ability': self.name,
                'is_ultimate': False
            })
            
            print(f"🎯 {context.caster.name} usó {self.name}!")
        
        return success
    
    def get_description(self):
        descriptions = []
        for effect in self.effects:
            if isinstance(effect, DamageEffect):
                multiplier = effect.config.get('multiplier', 1.0)
                if isinstance(multiplier, list):
                    min_dmg = int(multiplier[0] * 100)
                    max_dmg = int(multiplier[-1] * 100)
                    descriptions.append(f"Daño cadena: {min_dmg}%-{max_dmg}% ATQ")
                else:
                    descriptions.append(f"Daño: {int(multiplier * 100)}% ATQ")
            elif isinstance(effect, HealEffect):
                amount = effect.config.get('amount', 0)
                descriptions.append(f"Curación: {amount} HP")
            elif isinstance(effect, MovementEffect):
                move_type = effect.config.get('move_type', 'teleport')
                range_distance = effect.config.get('range', 1)
                if move_type == 'teleport':
                    descriptions.append(f"Teletransporte: {range_distance} casillas")
                elif move_type == 'post_action':
                    descriptions.append(f"Movimiento posterior: {range_distance} casillas")
        return " | ".join(descriptions) if descriptions else "Habilidad especial"

class UltimateAbility(ComposableAbility):
    """Habilidad definitiva que requiere energía específica"""
    
    def __init__(self, ability_config):
        super().__init__(ability_config)
        self.energy_cost = ability_config.get('energy_cost', 100)
        self.is_ultimate = True
    
    def can_execute(self, context):
        base_can_execute = super().can_execute(context)
        if not base_can_execute:
            return False
        
        if not context.caster.can_use_ultimate(self.ability_config):
            current_energy = context.caster.get_energy_absolute()
            print(f"❌ Energía insuficiente: {current_energy}/{self.energy_cost}")
            return False
        
        return True
    
    def execute(self, context):
        if not self.can_execute(context):
            return False
        
        if not context.caster.consume_ultimate_energy(self.energy_cost):
            return False
        
        context.ability_name = self.name
        success = False
        
        for effect in self.effects:
            if effect.apply(context):
                success = True
        
        if success:
            context.caster.has_acted = True
            context.caster.stats['current_ph'] -= self.cost_ph
            
            event_system.emit(EventTypes.ABILITY_USED, {
                'caster': context.caster,
                'ability': self.name,
                'is_ultimate': True,
                'energy_cost': self.energy_cost
            })
            
            print(f"💥💥💥 {context.caster.name} usó ULTIMATE: {self.name}!")
        
        return success

class AbilityFactory:
    """Factory que crea habilidades normales y definitivas"""
    
    @staticmethod
    def create_ability(ability_config):
        if ability_config.get('is_ultimate', False):
            return UltimateAbility(ability_config)
        return ComposableAbility(ability_config)