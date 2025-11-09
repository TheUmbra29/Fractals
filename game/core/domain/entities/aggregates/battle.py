from typing import List, Dict, Optional, Set
from uuid import UUID, uuid4
from ..value_objects.entity_id import EntityId 
from ..value_objects.position import Position  
from ..battle_entity import BattleEntity
from ...events.domain_event import DomainEvent
from ...events.player_turn_started import PlayerTurnStarted
from ...events.player_turn_ended import PlayerTurnEnded
from ...events.enemy_turn_started import EnemyTurnStarted
from ...events.enemy_turn_ended import EnemyTurnEnded

class Battle:
    """AGREGADO RAIZ - Representa una batalla completa en FRACTALS"""
    
    def __init__(self, battle_id: UUID, mode: str = "arcade", grid_size: tuple = (8, 8)):
        self._id = battle_id
        self._mode = mode  # "tutorial", "arcade"
        self._grid_size = grid_size
        self._entities: Dict[EntityId, BattleEntity] = {}
        self._obstacles: Set[Position] = set()  # Estructuras de cobertura
        self._current_turn = "player"  # "player" | "enemy"
        self._turn_count = 1
        self._actions_remaining = 3  # 3 acciones por turno según GDD
        self._pending_events: List[DomainEvent] = []
        
        # Estado específico de FRACTALS
        self._wave_number = 1  # Para modo arcade
        self._is_completed = False

    # PROPIEDADES DE SOLO LECTURA
    @property
    def id(self) -> UUID:
        return self._id

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def grid_size(self) -> tuple:
        return self._grid_size

    @property
    def current_turn(self) -> str:
        return self._current_turn

    @property
    def turn_count(self) -> int:
        return self._turn_count

    @property
    def actions_remaining(self) -> int:
        return self._actions_remaining

    @property
    def wave_number(self) -> int:
        return self._wave_number

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    # GESTIÓN DE ENTIDADES
    def add_entity(self, entity: BattleEntity) -> None:
        """Añade una entidad a la batalla"""
        self._entities[entity.id] = entity

    def get_entity(self, entity_id: EntityId) -> Optional[BattleEntity]:
        """Obtiene una entidad por su ID"""
        return self._entities.get(entity_id)

    def get_player_entities(self) -> List[BattleEntity]:
        """Obtiene todas las entidades del jugador"""
        return [entity for entity in self._entities.values() if entity.team == "player"]

    def get_enemy_entities(self) -> List[BattleEntity]:
        """Obtiene todas las entidades enemigas"""
        return [entity for entity in self._entities.values() if entity.team == "enemy"]

    def get_alive_player_entities(self) -> List[BattleEntity]:
        """Obtiene entidades del jugador que están vivas"""
        return [entity for entity in self.get_player_entities() if entity.stats.is_alive()]

    def get_alive_enemy_entities(self) -> List[BattleEntity]:
        """Obtiene entidades enemigas que están vivas"""
        return [entity for entity in self.get_enemy_entities() if entity.stats.is_alive()]

    # GESTIÓN DE OBSTÁCULOS/COBERTURA
    def add_obstacle(self, position: Position) -> None:
        """Añade una posición de obstáculo/cobertura"""
        self._obstacles.add(position)

    def is_obstacle(self, position: Position) -> bool:
        """Verifica si una posición tiene un obstáculo"""
        return position in self._obstacles

    # GESTIÓN DE TURNOS Y ACCIONES (NÚCLEO DE FRACTALS)
    def consume_player_action(self) -> List[DomainEvent]:
        """
        Consume una acción del jugador según GDD de FRACTALS
        Retorna eventos si el turno termina
        """
        if self._current_turn != "player":
            raise InvalidTurnError("No es el turno del jugador")
            
        if self._actions_remaining <= 0:
            raise NoActionsRemainingError("No quedan acciones este turno")

        self._actions_remaining -= 1
        events = []
        
        # Si no quedan acciones, terminar turno automáticamente
        if self._actions_remaining <= 0:
            events.extend(self._end_player_turn())
            
        return events

    def _end_player_turn(self) -> List[DomainEvent]:
        """Finaliza el turno del jugador y pasa al turno de la IA"""
        events = [PlayerTurnEnded(self._id, self._turn_count)]
        
        # Resetear estado de todas las entidades aliadas
        for entity in self.get_player_entities():
            entity.reset_turn_state()
            
        # Cambiar a turno de la IA
        self._current_turn = "enemy"
        events.append(EnemyTurnStarted(self._id, self._turn_count))
        
        # En un futuro, aquí se ejecutaría la lógica de IA
        # Por ahora, terminamos inmediatamente el turno enemigo
        events.extend(self._end_enemy_turn())
        
        return events

    def _end_enemy_turn(self) -> List[DomainEvent]:
        """Finaliza el turno de la IA y pasa al siguiente turno del jugador"""
        events = [EnemyTurnEnded(self._id, self._turn_count)]
        
        # Resetear estado de todas las entidades enemigas
        for entity in self.get_enemy_entities():
            entity.reset_turn_state()
            
        # Preparar nuevo turno del jugador
        self._current_turn = "player"
        self._turn_count += 1
        self._actions_remaining = 3  # Resetear a 3 acciones
        
        events.append(PlayerTurnStarted(self._id, self._turn_count))
        
        # Verificar condiciones de victoria/derrota
        victory_events = self._check_battle_conditions()
        events.extend(victory_events)
        
        return events

    def _check_battle_conditions(self) -> List[DomainEvent]:
        """Verifica condiciones de victoria/derrota según el modo"""
        events = []
        
        alive_players = self.get_alive_player_entities()
        alive_enemies = self.get_alive_enemy_entities()
        
        # Modo Arcade: oleadas infinitas
        if self._mode == "arcade" and len(alive_enemies) == 0:
            self._wave_number += 1
            # En el futuro: generar nueva oleada de enemigos
            # events.append(NewWaveStarted(self._id, self._wave_number))
        
        # Victoria: todos los enemigos eliminados
        if len(alive_enemies) == 0:
            self._is_completed = True
            # events.append(BattleVictory(self._id))
            
        # Derrota: todos los jugadores eliminados  
        if len(alive_players) == 0:
            self._is_completed = True
            # events.append(BattleDefeat(self._id))
            
        return events

    # UTILIDADES
    def is_position_valid(self, position: Position) -> bool:
        """Verifica si una posición está dentro del grid"""
        return (0 <= position.x < self._grid_size[0] and 
                0 <= position.y < self._grid_size[1])

    def is_position_occupied(self, position: Position) -> bool:
        """Verifica si una posición está ocupada por una entidad"""
        return any(entity.position == position for entity in self._entities.values())

    def get_entity_at_position(self, position: Position) -> Optional[BattleEntity]:
        """Obtiene la entidad en una posición específica"""
        for entity in self._entities.values():
            if entity.position == position:
                return entity
        return None

    def clear_events(self) -> List[DomainEvent]:
        """Obtiene y limpia los eventos pendientes"""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events

    def __repr__(self) -> str:
        return f"Battle(mode={self._mode}, turn={self._turn_count}, actions={self._actions_remaining}, entities={len(self._entities)})"

# EXCEPCIONES ESPECÍFICAS DEL DOMINIO
class InvalidTurnError(Exception):
    pass

class NoActionsRemainingError(Exception):
    pass