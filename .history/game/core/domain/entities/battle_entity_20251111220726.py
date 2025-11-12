from typing import List, Optional, Set, Dict
from uuid import UUID

from .value_objects.position import Position
from .value_objects.stats import EntityStats
from .value_objects.entity_id import EntityId
from .value_objects.progression import Progression
from .habilidad import Habilidad, TipoHabilidad
from .value_objects.game_enums import Team, CharacterClass, ActionType
from ..events.domain_event import DomainEvent
from ..events.entity_damaged import EntityDamaged
from ..events.entity_died import EntityDied
from ..events.dash_executed import DashExecuted
from ..config.game_config import GAME_CONFIG

# Definir placeholders localmente para evitar importación circular
class EntityLeveledUp(DomainEvent):
    def __init__(self, entity_id, old_level, new_level):
        self.entity_id = entity_id
        self.old_level = old_level
        self.new_level = new_level

class BattleEntity:
    """ENTIDAD RAIZ usando enums y configuración"""

    def __init__(self, entity_id: EntityId, position: Position, stats: EntityStats, 
                 team: Team, name: str, character_class: CharacterClass, habilidades: Dict[str, Habilidad] = None):
        self._id = entity_id
        self._position = position
        self._stats = stats
        self._team = team
        self._name = name
        self._character_class = character_class
        self._pending_events: List[DomainEvent] = []
        # Estado temporal del turno
        self._has_acted = False
        self._has_moved = False
        self._actions_used_this_turn: Set[ActionType] = set()
        self._dash_targets_this_move: Set[EntityId] = set()
        self._progression = Progression()
        self._habilidades = habilidades or self._get_default_habilidades()

    # PROPIEDADES DE SOLO LECTURA
    @property
    def id(self) -> EntityId:
        return self._id
    
    @property
    def position(self) -> Position:
        return self._position
    
    @property
    def stats(self) -> EntityStats:
        return self._stats
    
    @property
    def team(self) -> str:
        return self._team
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def character_class(self) -> str:
        return self._character_class
    
    @property
    def has_acted(self) -> bool:
        return self._has_acted
    
    @property
    def has_moved(self) -> bool:
        return self._has_moved
    
    @property
    def actions_used_this_turn(self) -> Set[str]:
        return self._actions_used_this_turn
    
    @property
    def dash_targets_this_move(self) -> Set[EntityId]:
        return self._dash_targets_this_move
    
    @property
    def progression(self) -> Progression:
        return self._progression
    
    @property
    def habilidades(self) -> Dict[str, Habilidad]:
        return self._habilidades.copy()
    
    @property
    def current_ph(self) -> int:
        return self._stats.current_ph
    
    @property
    def max_ph(self) -> int:
        return self._stats.max_ph

    # COMPORTAMIENTO DEL DOMINIO
    def take_damage(self, damage_amount: int) -> List[DomainEvent]:
        """COMMAND: Modifica estado y produce eventos de dominio"""
        if not self._stats.is_alive():
            return []  # Entidades muertas no reciben daño
            
        old_hp = self._stats.current_hp
        self._stats = self._stats.reduce_hp(damage_amount)
        
        events = [EntityDamaged(
            entity_id=self._id,
            old_hp=old_hp,
            new_hp=self._stats.current_hp,
            damage_amount=damage_amount
        )]
        
        if not self._stats.is_alive():
            events.append(EntityDied(entity_id=self._id))
            
        self._pending_events.extend(events)
        return events

    def move_to(self, new_position: Position) -> None:
        """COMMAND: Mueve la entidad a una nueva posición"""
        if self._has_moved:
            raise ValueError(f"{self._name} ya se ha movido este turno")
            
        self._position = new_position
        self._has_moved = True
        self.mark_action_used("move")

    def execute_dash_attack(self, enemy: 'BattleEntity') -> List[DomainEvent]:
        """Embestida - mecánica central de FRACTALS"""
        if enemy.id in self._dash_targets_this_move:
            return []  # No embestir mismo enemigo dos veces en un mismo movimiento
            
        # Daño fijo de 15 según especificaciones
        dash_damage = 15
        events = enemy.take_damage(dash_damage)
        self._dash_targets_this_move.add(enemy.id)
        
        events.append(DashExecuted(self.id, enemy.id, dash_damage))
        self._pending_events.extend(events)
        return events

    def mark_action_used(self, action_type: str) -> None:
        """Marca que se usó una acción este turno"""
        self._actions_used_this_turn.add(action_type)

    def can_perform_action(self, action_type: str) -> bool:
        """Según GDD: múltiples acciones pero no repetidas"""
        return action_type not in self._actions_used_this_turn

    def gain_experience(self, amount: int) -> List[DomainEvent]:
        """Progresión temporal - se reinicia al terminar sesión"""
        old_level = self._progression.level
        new_progression = self._progression.add_experience(amount)
        
        events = []
        if new_progression.level > old_level:
            events.append(EntityLeveledUp(self.id, old_level, new_progression.level))
            # Aquí podríamos aplicar mejoras de nivel (aumentar stats, etc.)
            
        self._progression = new_progression
        self._pending_events.extend(events)
        return events

    def reset_turn_state(self) -> None:
        """COMMAND: Prepara la entidad para nuevo turno"""
        self._has_acted = False
        self._has_moved = False
        self._actions_used_this_turn.clear()
        self._dash_targets_this_move.clear()
        
        # Recuperar 20% de PH al inicio del turno (según balance del GDD)
        ph_recovery = int(self._stats.max_ph * 0.2)
        self.restore_ph(ph_recovery)
        
        # Reducir cooldowns de habilidades
        self.reduce_ability_cooldowns()

    def clear_events(self) -> List[DomainEvent]:
        """Obtiene y limpia eventos pendientes"""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events

    # SISTEMA DE HABILIDADES CON PH Y TdE
    def _get_default_abilities(self) -> Dict[str, Ability]:
        """Habilidades por defecto usando configuración de clases y enums"""
        base_abilities = {
            str(ActionType.BASIC_ATTACK): Ability(
                id=AbilityId.generate(),
                name="Ataque Básico",
                description="Ataque básico sin costo de PH",
                ph_cost=0,
                cooldown_turns=0,
                damage_multiplier=1.0,
                range=1
            )
        }
        class_config = GAME_CONFIG.CLASS_STATS.get(str(self._character_class), {})
        if self._character_class == CharacterClass.DAMAGE:
            base_abilities.update({
                str(ActionType.ABILITY_ALPHA): Ability(
                    id=AbilityId.generate(),
                    name="Golpe Frenético",
                    description=f"Ataque rápido - Daño: {class_config.get('attack', 25) * 1.5}",
                    ph_cost=20,
                    cooldown_turns=1,
                    damage_multiplier=1.5,
                    range=2
                ),
                # ... otras habilidades
            })
        # ... otras clases
        return base_abilities

    def can_use_ability(self, ability_type: str) -> bool:
        """Verifica si puede usar una habilidad según PH y TdE"""
        if ability_type not in self._abilities:
            return False
            
        ability = self._abilities[ability_type]
        
        # Verificar PH suficiente
        if self._stats.current_ph < ability.ph_cost:
            return False
            
        # Verificar que no esté en cooldown
        if ability.current_cooldown > 0:
            return False
            
        # Verificar que no haya usado esta habilidad este turno (según GDD)
        if ability_type in self._actions_used_this_turn:
            return False
            
        return True

    def use_ability(self, ability_type: str, target: Optional['BattleEntity'] = None) -> List[DomainEvent]:
        """Usa una habilidad, consumiendo PH y aplicando cooldown"""
        if ability_type not in self._abilities:
            raise ValueError(f"Habilidad {ability_type} no existe")
            
        ability = self._abilities[ability_type]
        
        if not self.can_use_ability(ability_type):
            raise ValueError(f"No puede usar {ability_type}")
        
        events = []
        
        # Consumir PH
        if ability.ph_cost > 0:
            self._stats = self._stats.reduce_ph(ability.ph_cost)
        
        # Aplicar cooldown
        self._abilities[ability_type] = ability.use()
        
        # Marcar como usada este turno
        self.mark_action_used(ability_type)
        
        # Aplicar efecto de la habilidad
        if target and ability.damage_multiplier != 0:
            if ability.damage_multiplier > 0:
                # Habilidad de daño
                damage = int(self._stats.attack * ability.damage_multiplier)
                damage_events = target.take_damage(damage)
                events.extend(damage_events)
            else:
                # Habilidad de curación/escudo (placeholder)
                heal_amount = int(self._stats.attack * abs(ability.damage_multiplier))
                # Aquí iría la lógica de curación - por ahora solo evento
                from ..events.entity_healed import EntityHealed
                events.append(EntityHealed(
                    entity_id=target.id,
                    heal_amount=heal_amount,
                    healer_id=self._id
                ))
        
        self._pending_events.extend(events)
        return events

    def reduce_ability_cooldowns(self):
        """Reduce todos los cooldowns en 1 (llamar al final del turno)"""
        for ability_type, ability in self._abilities.items():
            if ability.current_cooldown > 0:
                self._abilities[ability_type] = ability.reduce_cooldown()

    def restore_ph(self, amount: int):
        """Restaura PH (hasta el máximo)"""
        new_ph = min(self._stats.max_ph, self._stats.current_ph + amount)
        self._stats = EntityStats(
            max_hp=self._stats.max_hp,
            current_hp=self._stats.current_hp,
            max_ph=self._stats.max_ph,
            current_ph=new_ph,
            attack=self._stats.attack,
            defense=self._stats.defense,
            speed=self._stats.speed
        )

    # IGUALDAD POR IDENTIDAD
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BattleEntity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"BattleEntity({self._name}, {self._position}, HP: {self._stats.current_hp}/{self._stats.max_hp})"