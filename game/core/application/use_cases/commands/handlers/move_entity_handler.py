from .....domain.repositories.battle_repository import BattleRepository
from .....domain.services.movement_validation_service import MovementValidationService
from ..move_entity_command import MoveEntityCommand

class MoveEntityHandler:
    """Manejador para el comando de mover entidad"""
    
    def __init__(self, battle_repository: BattleRepository):
        self.battle_repository = battle_repository
    
    def handle(self, command: MoveEntityCommand):
        # 1. Cargar el agregado Battle
        battle = self.battle_repository.get_by_id(command.battle_id)
        
        # 2. Obtener la entidad
        entity = battle.get_entity(command.entity_id)
        if not entity:
            raise ValueError("Entidad no encontrada")
        
        # 3. Validar movimiento
        obstacles = battle._obstacles
        all_entities = list(battle._entities.values())
        if not MovementValidationService.validate_movement_path(
            entity.position, command.target_position, obstacles, all_entities
        ):
            raise ValueError("Movimiento no válido")
        
        # 4. Mover la entidad
        entity.move_to(command.target_position)
        
        # 5. Procesar embestidas
        events = []
        for enemy_id in command.dash_targets:
            enemy = battle.get_entity(enemy_id)
            if enemy and enemy.team != entity.team:
                dash_events = entity.execute_dash_attack(enemy)
                events.extend(dash_events)
        
        # 6. Marcar acción usada
        entity.mark_action_used("move")
        
        # 7. Consumir acción del turno
        battle.consume_player_action()
        
        # 8. Guardar cambios
        self.battle_repository.save(battle)
        
        # 9. Devolver eventos
        return events