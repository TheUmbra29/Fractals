"""
SERVICIO DE TURNOS - En la ubicación REAL
"""
from typing import List
from .route_system import RouteSystem
from ..entities.value_objects.position import Position
from .route_system import MovementRoute
from ..entities.value_objects.entity_id import EntityId

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
    
    def execute_movement_with_dashes(self, battle_id, entity_id, target_position: Position, 
                                   marked_dash_targets: List[EntityId] = None) -> str:
        """Ejecuta movimiento con embestidas MANUALES según tu GDD"""
        if marked_dash_targets is None:
            marked_dash_targets = []

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

        # FILTRAR embestidas: solo las marcadas manualmente + máximo 1 por enemigo
        valid_dash_targets = []
        dash_target_ids = set()
        
        for enemy in route.dash_targets:
            # Solo incluir si fue marcado manualmente Y no ha sido embestido aún
            if (enemy.id in marked_dash_targets and 
                enemy.id not in dash_target_ids and
                enemy.id not in entity.dash_targets_this_move):
                
                valid_dash_targets.append(enemy)
                dash_target_ids.add(enemy.id)

        # Ejecutar movimiento
        entity.move_to(target_position)

        # Ejecutar embestidas MANUALES filtradas
        dash_results = []
        for enemy in valid_dash_targets:
            try:
                events = entity.execute_dash_attack(enemy)
                dash_results.append({
                    "enemy": enemy.name,
                    "damage": 15,  # Daño fijo según GDD
                    "success": True
                })
            except Exception as e:
                dash_results.append({
                    "enemy": enemy.name, 
                    "error": str(e),
                    "success": False
                })

        # Consumir acción de movimiento
        battle.consume_player_action()
        self.battle_repo.save(battle)

        # Construir mensaje de resultado
        if dash_results:
            successful_dashes = [r for r in dash_results if r["success"]]
            if successful_dashes:
                enemies_list = ", ".join([r["enemy"] for r in successful_dashes])
                return f"{entity.name} se movió a {target_position} y embistió a: {enemies_list}"
            else:
                return f"{entity.name} se movió a {target_position} (embestidas fallidas)"
        else:
            return f"{entity.name} se movió a {target_position}"
        
    def execute_ability(self, battle_id, caster_id, ability_type: str, 
                       target_entity_id: EntityId = None) -> str:
        """Ejecuta una habilidad con validación de PH y TdE"""
        battle = self.battle_repo.get_by_id(battle_id)
        caster = battle.get_entity(caster_id)
        target_entity = battle.get_entity(target_entity_id) if target_entity_id else None

        if not caster:
            raise ValueError("Entidad no encontrada")

        # Validaciones básicas
        if battle.current_turn != "player":
            raise ValueError("No es el turno del jugador")

        if caster.team != "player":
            raise ValueError("Solo puedes usar habilidades con entidades del jugador")

        # Ejecutar habilidad
        try:
            events = caster.use_ability(ability_type, target_entity)
            
            # Consumir acción del turno
            battle.consume_player_action()
            self.battle_repo.save(battle)
            
            # Construir mensaje
            ability = caster.abilities[ability_type]
            if target_entity:
                if ability.damage_multiplier > 0:
                    return f"{caster.name} usa {ability.name} en {target_entity.name}"
                else:
                    return f"{caster.name} usa {ability.name} en {target_entity.name}"
            else:
                return f"{caster.name} usa {ability.name}"
                
        except Exception as e:
            raise ValueError(f"Error al usar habilidad: {e}")

    def get_ability_targets(self, battle_id, caster_id, ability_type: str) -> List[EntityId]:
        """Obtiene objetivos válidos para una habilidad"""
        battle = self.battle_repo.get_by_id(battle_id)
        caster = battle.get_entity(caster_id)
        
        if not caster or ability_type not in caster.abilities:
            return []
            
        ability = caster.abilities[ability_type]
        targets = []
        
        # Lógica simple de rango
        for entity in battle._entities.values():
            if entity.id == caster.id:
                continue
                
            distance = caster.position.distance_to(entity.position)
            if distance <= ability.range:
                # Validar tipo de objetivo según la habilidad
                if ability.damage_multiplier > 0:  # Habilidad de daño
                    if entity.team != caster.team:
                        targets.append(entity.id)
                else:  # Habilidad de curación/soporte
                    if entity.team == caster.team:
                        targets.append(entity.id)
        
        return targets