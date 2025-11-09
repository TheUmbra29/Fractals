from .....domain.repositories.battle_repository import BattleRepository
from ..end_turn_command import EndTurnCommand

class EndTurnHandler:
    """Manejador para terminar el turno"""
    
    def __init__(self, battle_repository: BattleRepository):
        self.battle_repository = battle_repository
    
    def handle(self, command: EndTurnCommand):
        battle = self.battle_repository.get_by_id(command.battle_id)
        
        # Forzar el fin del turno del jugador
        events = []
        while battle.actions_remaining > 0:
            turn_events = battle.consume_player_action()
            events.extend(turn_events)
        
        self.battle_repository.save(battle)
        return events