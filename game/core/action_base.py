# game/core/action_base.py
"""
Sistema base de acciones - PRAGMÁTICO Y ESCALABLE
Diseñado para funcionar HOY y crecer MAÑANA sin sobre-ingeniería
"""

class ActionContext:
    """Contexto unificado para ejecución de acciones"""
    
    def __init__(self, caster, target=None, target_position=None, entities=None, **kwargs):
        self.caster = caster
        self.target = target
        self.target_position = target_position
        self.entities = entities or []
        self.extra_data = kwargs
        self.ability_name = ""


class BaseAction:
    """
    Clase base CONCRETA con funcionalidad esencial.
    Proporciona defaults razonables y es extensible.
    """
    
    def __init__(self, name, action_type, cost_ph=0, cooldown=0, selection_mode="enemy", range=1):
        self.name = name
        self.type = action_type
        self.cost_ph = cost_ph
        self.cooldown = cooldown
        self.selection_mode = selection_mode
        self.range = range
        self.current_cooldown = 0
    
    def can_execute(self, context):
        """Validaciones base - overrideable por subclases si necesitan más validaciones"""
        # PH suficiente
        if context.caster.stats['current_ph'] < self.cost_ph:
            return False
        
        # Cooldown activo
        if self.current_cooldown > 0:
            return False
        
        # Estado del turno
        if self.type == 'movement' and context.caster.has_moved:
            return False
            
        if self.type == 'ability' and context.caster.has_acted:
            return False
            
        return True
    
    def execute(self, context):
        """
        Método de ejecución principal.
        Las subclases DEBEN override este método para su comportamiento específico.
        """
        raise NotImplementedError(f"{self.__class__.__name__} debe implementar execute()")
    
    def get_description(self):
        """Descripción para UI - overrideable por subclases"""
        return f"{self.name} - Costo: {self.cost_ph} PH - Rango: {self.range}"
    
    def get_range(self):
        """Rango de la acción"""
        return self.range
    
    def start_cooldown(self):
        """Inicia el cooldown si es necesario"""
        if self.cooldown > 0:
            self.current_cooldown = self.cooldown
    
    def update_cooldown(self):
        """Actualiza cooldown - llamar cada turno"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1