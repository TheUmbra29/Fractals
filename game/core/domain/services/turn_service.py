"""
SERVICIO DE TURNOS - En la ubicación REAL
"""
from typing import List
from .route_system import RouteSystem
from ..entities.value_objects.position import Position
from .route_system import MovementRoute

class TurnService:
    """Maneja la lógica de turnos"""
    
    def __init__(self, battle_repository):
        self.battle_repo = battle_repository
    
    def end_player_turn(self, battle_id) -> List:
        """Termina el turno del jugador"""
        battle = self.battle_repo.get_by_id(battle_id)
        
        if battle.current_turn != "player":
            raise ValueError("No es el turno del jugador")
        
        events = []
        actions_consumed = 0
        max_actions = battle.actions_remaining
        
        while battle.actions_remaining > 0 and actions_consumed < max_actions:
            turn_events = battle.consume_player_action()
            events.extend(turn_events)
            actions_consumed += 1
        
        self.battle_repo.save(battle)
        return events
    
    def move_entity(self, battle_id, entity_id, target_position: Position) -> str:
        """Mueve una entidad"""
        battle = self.battle_repo.get_by_id(battle_id)
        entity = battle.get_entity(entity_id)
        
        if not entity:
            raise ValueError("Entidad no encontrada")
        
        if entity.team != "player":
            raise ValueError("Solo puedes mover entidades del jugador")
        
        if battle.current_turn != "player":
            raise ValueError("No es el turno del jugador")
        
        if entity.has_moved:
            raise ValueError("Esta entidad ya se movió este turno")
        
        # Validar movimiento
        if not battle.is_position_valid(target_position):
            raise ValueError("Posición fuera del grid")
        
        if battle.is_position_occupied(target_position):
            raise ValueError("Posición ocupada")
        
        if battle.is_obstacle(target_position):
            raise ValueError("Hay un obstáculo en esa posición")
        
        # Ejecutar movimiento
        entity.move_to(target_position)
        battle.consume_player_action()
        
        self.battle_repo.save(battle)
        return f"{entity.name} movido a {target_position}"
    
    def get_valid_moves(self, battle_id, entity_id) -> List[Position]:
        """Obtiene movimientos válidos para una entidad"""
        battle = self.battle_repo.get_by_id(battle_id)
        entity = battle.get_entity(entity_id)
        
        if not entity or entity.team != "player":
            return []
        
        valid_positions = []
        movement_range = 3
        
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                if abs(dx) + abs(dy) <= movement_range:
                    new_pos = Position(entity.position.x + dx, entity.position.y + dy)
                    
                    if (battle.is_position_valid(new_pos) and
                        not battle.is_position_occupied(new_pos) and
                        not battle.is_obstacle(new_pos)):
                        valid_positions.append(new_pos)
        
        return valid_positions
    
    def calculate_movement_route(self, battle_id, entity_id, target_position: Position) -> MovementRoute:
        """Calcula y retorna una ruta sin ejecutarla (para previsualización)"""
        battle = self.battle_repo.get_by_id(battle_id)
        entity = battle.get_entity(entity_id)
        
        if not entity:
            raise ValueError("Entidad no encontrada")
            
        return RouteSystem.calculate_route(entity.position, target_position, battle, entity)
    
    def execute_movement_with_dashes(self, battle_id, entity_id, target_position: Position) -> str:
        """Ejecuta movimiento completo con embestidas automáticas"""
        battle = self.battle_repo.get_by_id(battle_id)
        entity = battle.get_entity(entity_id)
        
        # Validaciones básicas
        if not entity or entity.team != "player" or battle.current_turn != "player" or entity.has_moved:
            raise ValueError("Movimiento no válido")
        
        # Calcular ruta
        route = RouteSystem.calculate_route(entity.position, target_position, battle, entity)
        
        if not route.path:
            raise ValueError("No hay ruta válida hacia la posición objetivo")
            
        if not route.is_valid:
            raise ValueError("La ruta excede el límite de velocidad")
        
        # Ejecutar movimiento
        entity.move_to(target_position)
        
        # Ejecutar embestidas
        dash_events = []
        for enemy in route.dash_targets:
            events = entity.execute_dash_attack(enemy)
            dash_events.extend(events)
        
        # Consumir acción
        battle.consume_player_action()
        self.battle_repo.save(battle)
        
        # Mensaje de resultado
        if route.dash_targets:
            return f"{entity.name} se movió a {target_position} y embistió a {len(route.dash_targets)} enemigos ({-route.dash_damage} daño total)"
        else:
            return f"{entity.name} se movió a {target_position}"