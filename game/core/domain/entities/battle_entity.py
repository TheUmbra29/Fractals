from typing import List, Optional, Set
from uuid import UUID
from .value_objects.position import Position
from .value_objects.stats import EntityStats
from .value_objects.entity_id import EntityId
from .value_objects.progression import Progression
from ..events.domain_event import DomainEvent
from ..events.entity_damaged import EntityDamaged
from ..events.entity_died import EntityDied

# Importaciones para eventos específicos de FRACTALS
try:
    from ..events.dash_executed import DashExecuted
    from ..events.entity_leveled_up import EntityLeveledUp
except ImportError:
    # Placeholders si los eventos no existen todavía
    class DashExecuted(DomainEvent): pass
    class EntityLeveledUp(DomainEvent): pass

class BattleEntity:
    """ENTIDAD RAIZ con identidad y ciclo de vida propio para FRACTALS"""
    
    def __init__(self, entity_id: EntityId, position: Position, stats: EntityStats, team: str, name: str, character_class: str):
        self._id = entity_id
        self._position = position
        self._stats = stats
        self._team = team
        self._name = name
        self._character_class = character_class
        self._pending_events: List[DomainEvent] = []
        
        # Estado temporal del turno (se resetea cada turno)
        self._has_acted = False
        self._has_moved = False
        self._actions_used_this_turn: Set[str] = set()  # Tipos de acción usados este turno
        self._dash_targets_this_move: Set[EntityId] = set()  # IDs de enemigos embestidos en este movimiento

        # Progresión temporal (se reinicia al terminar la sesión)
        self._progression = Progression()

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
        """COMMAND: Mueve la entidad (sin eventos por ahora)"""
        if self._has_moved:
            raise ValueError(f"{self._name} ya se ha movido este turno")
            
        self._position = new_position
        self._has_moved = True

    def execute_dash_attack(self, enemy: 'BattleEntity') -> List[DomainEvent]:
        """Embestida - mecánica central de FRACTALS"""
        if enemy.id in self._dash_targets_this_move:
            return []  # No embestir mismo enemigo dos veces en un mismo movimiento
            
        # Calculamos el daño de la embestida (10% del ataque)
        dash_damage = max(1, int(self.stats.attack * 0.1))
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
            # Por ahora, solo el evento
            
        self._progression = new_progression
        self._pending_events.extend(events)
        return events

    def reset_turn_state(self) -> None:
        """COMMAND: Prepara la entidad para nuevo turno"""
        self._has_acted = False
        self._has_moved = False
        self._actions_used_this_turn.clear()
        self._dash_targets_this_move.clear()

    def clear_events(self) -> List[DomainEvent]:
        """Obtiene y limpia eventos pendientes"""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events

    # IGUALDAD POR IDENTIDAD
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BattleEntity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"BattleEntity({self._name}, {self._position}, HP: {self._stats.current_hp}/{self._stats.max_hp})"