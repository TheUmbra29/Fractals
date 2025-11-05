from .base_action import BaseAction, ActionContext
from game.core.event_system import event_system, EventTypes

class MoveAction(BaseAction):
    def __init__(self):
        super().__init__("move", "movement", cost_ph=0)
    
    def can_execute(self, context):
        return False  # 🎯 Deshabilitado - se usa el sistema con línea
    
    def execute(self, context):
        return False  # 🎯 Deshabilitado - se usa el sistema con línea