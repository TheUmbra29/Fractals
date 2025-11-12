from uuid import uuid4
from ..value_objects.position import Position
from game.core.domain.services.cover_system import CoverType

def setup_test_battle():
    battle = Battle(battle_id=uuid4())
    # Añadir cobertura para testing
    battle.cover_system.add_cover_structure(Position(2, 2), CoverType.FULL)
    battle.cover_system.add_cover_structure(Position(5, 5), CoverType.HALF)
    battle.cover_system.add_cover_structure(Position(8, 3), CoverType.FULL)
    return battle
from typing import List, Dict, Optional, Set
from uuid import UUID, uuid4

from ..value_objects.entity_id import EntityId 
from ..value_objects.position import Position  
from ..value_objects.game_enums import Team, GameState
from ..battle_entity import BattleEntity
from ...events.domain_event import DomainEvent
from ...events.player_turn_started import PlayerTurnStarted
from ...events.player_turn_ended import PlayerTurnEnded
from ...events.enemy_turn_started import EnemyTurnStarted
from ...events.enemy_turn_ended import EnemyTurnEnded
from ...config.game_config import GAME_CONFIG
from game.core.domain.services.cover_system import CoverSystem, CoverType

class Battle:
    """AGREGADO RAIZ - Representa una batalla completa en FRACTALS"""
    
    def __init__(self, battle_id: UUID, mode: str = "arcade", grid_size: tuple = None):
        self._id = battle_id
        self._mode = mode
        self._grid_size = grid_size or GAME_CONFIG.GRID_SIZE
        self._entities: Dict[EntityId, BattleEntity] = {}
        self._obstacles: Set[Position] = set()
        self._current_turn = Team.PLAYER
        self._turn_count = 1
        self._actions_remaining = GAME_CONFIG.ACTIONS_PER_TURN
        self._pending_events: List[DomainEvent] = []
        self._wave_number = 1
        self._is_completed = False
        self.cover_system = CoverSystem()
        self._initialize_cover_structures()

    def _initialize_cover_structures(self):
        """Inicializa las estructuras de cobertura en el mapa"""
        self.cover_system.add_cover_structure(Position(3, 3), CoverType.FULL)
        self.cover_system.add_cover_structure(Position(7, 5), CoverType.HALF)
        self.cover_system.add_cover_structure(Position(10, 8), CoverType.FULL)

    def calculate_attack(self, attacker, defender, ability=None):
        """Calcula el resultado de un ataque considerando cobertura"""
        hit_probability = self.cover_system.get_hit_probability(
            attacker.position, 
            defender.position
        )
        import random
        if random.random() <= hit_probability:
            damage = attacker.stats.attack - defender.stats.defense
            damage = max(1, damage)
            defender.stats.current_hp -= damage
            return f"¡Ataque exitoso! {damage} de daño"
        else:
            cover_status = self.cover_system.get_cover_status(
                attacker.position, 
                defender.position
            )
            if cover_status == CoverType.FULL:
                return "¡El ataque fue bloqueado por cobertura total!"
            else:
                return "¡El ataque fue parcialmente bloqueado!"

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
    def current_turn(self) -> Team:
        return self._current_turn
    # NUEVOS MÉTODOS PÚBLICOS PARA ENCAPSULAMIENTO
    def get_entities(self) -> List[BattleEntity]:
        """Obtiene todas las entidades (copia)"""
        return list(self._entities.values())

    def get_obstacles(self) -> Set[Position]:
        """Obtiene todos los obstáculos (copia)"""
        return self._obstacles.copy()

    def get_entity_count(self) -> int:
        """Número total de entidades"""
        return len(self._entities)

    def get_alive_entities_by_team(self, team: Team) -> List[BattleEntity]:
        """Obtiene entidades vivas de un equipo específico"""
        return [entity for entity in self._entities.values() 
                if entity.team == team and entity.stats.is_alive()]

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
        return [entity for entity in self._entities.values() 
                if entity.team == Team.PLAYER]

    def get_enemy_entities(self) -> List[BattleEntity]:
        """Obtiene todas las entidades enemigas"""
        return [entity for entity in self._entities.values() 
                if entity.team == Team.ENEMY]

    def get_alive_player_entities(self) -> List[BattleEntity]:
        """Obtiene entidades del jugador que están vivas"""
        return self.get_alive_entities_by_team(Team.PLAYER)

    def get_alive_enemy_entities(self) -> List[BattleEntity]:
        """Obtiene entidades enemigas que están vivas"""
        return self.get_alive_entities_by_team(Team.ENEMY)

    # GESTIÓN DE OBSTÁCULOS/COBERTURA
    def add_obstacle(self, position: Position) -> None:
        """Añade una posición de obstáculo/cobertura"""
        self._obstacles.add(position)

    def is_obstacle(self, position: Position) -> bool:
        """Verifica si una posición tiene un obstáculo"""
        return position in self._obstacles

    # GESTIÓN DE TURNOS Y ACCIONES (NÚCLEO DE FRACTALS)
    def consume_player_action(self) -> List[DomainEvent]:
        """Consume una acción del jugador usando configuración"""
        if self._current_turn != Team.PLAYER:
            raise InvalidTurnError("No es el turno del jugador")
        if self._actions_remaining <= 0:
            raise NoActionsRemainingError("No quedan acciones este turno")
        self._actions_remaining -= 1
        events = []
        if self._actions_remaining <= 0:
            events.extend(self._end_player_turn())
        return events

    def _end_player_turn(self) -> List[DomainEvent]:
        """Finaliza el turno del jugador"""
        events = [PlayerTurnEnded(self._id, self._turn_count)]
        for entity in self.get_player_entities():
            entity.reset_turn_state()
        self._current_turn = Team.ENEMY
        events.append(EnemyTurnStarted(self._id, self._turn_count))
        events.extend(self._end_enemy_turn())
        return events

    def _end_enemy_turn(self) -> List[DomainEvent]:
        """Finaliza el turno de la IA"""
        events = [EnemyTurnEnded(self._id, self._turn_count)]
        for entity in self.get_enemy_entities():
            entity.reset_turn_state()
        self._current_turn = Team.PLAYER
        self._turn_count += 1
        self._actions_remaining = GAME_CONFIG.ACTIONS_PER_TURN
        events.append(PlayerTurnStarted(self._id, self._turn_count))
        events.extend(self._check_battle_conditions())
        return events
    def is_position_occupied_by_ally(self, position: Position, entity: BattleEntity) -> bool:
        """Verifica si una posición está ocupada por un aliado"""
        for other_entity in self._entities.values():
            if (other_entity.position == position and 
                other_entity.team == entity.team and
                other_entity.id != entity.id):
                return True
        return False

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