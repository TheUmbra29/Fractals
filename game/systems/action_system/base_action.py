class BaseAction:
    """Clase base para TODAS las acciones del juego - MEJORADA"""
    
    # Metadata por defecto para el registry
    DEFAULT_DESCRIPTION = "Habilidad especial"
    DEFAULT_RANGE = 1
    
    def __init__(self, name, action_type, cost_ph=0, cooldown=0):
        self.name = name
        self.type = action_type
        self.cost_ph = cost_ph
        self.cooldown = cooldown
        self.current_cooldown = 0
    
    @classmethod
    def get_default_description(cls):
        return cls.DEFAULT_DESCRIPTION
    
    @classmethod 
    def get_default_range(cls):
        return cls.DEFAULT_RANGE
    
    def get_description(self):
        """Las subclases pueden override este método para descripción específica por instancia"""
        return self.__class__.get_default_description()
    
    def get_range(self):
        """Las subclases pueden override este método para rango específico por instancia"""
        return self.__class__.get_default_range()
    
    def __init__(self, name, action_type, cost_ph=0, cooldown=0):
        self.name = name
        self.type = action_type
        self.cost_ph = cost_ph
        self.cooldown = cooldown
        self.current_cooldown = 0
    
    def can_execute(self, context):
        """🆕 NUEVO: Usa un contexto en lugar de parámetros sueltos"""
        # Validaciones base
        if context.caster.stats['current_ph'] < self.cost_ph:
            return False
        
        if self.current_cooldown > 0:
            return False
            
        if self.type == 'movement' and context.caster.has_moved:
            return False
            
        if self.type == 'attack' and context.caster.has_acted:
            return False
            
        return True
    
    def execute(self, context):
        """🆕 NUEVO: Ejecuta con contexto unificado"""
        raise NotImplementedError("Las subclases deben implementar execute()")
    
    def start_cooldown(self):
        self.current_cooldown = self.cooldown
    
    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class ActionContext:
    """🆕 NUEVA CLASE: Contexto unificado para ejecución de habilidades"""
    
    def __init__(self, caster, target=None, target_position=None, entities=None, **kwargs):
        self.caster = caster
        self.target = target
        self.target_position = target_position
        self.entities = entities or []
        self.extra_data = kwargs  # Datos adicionales para habilidades especiales
    
    def validate_target(self, required_team=None):
        """Valida que el target sea apropiado"""
        if not self.target:
            return False
        
        if required_team and self.target.team != required_team:
            return False
            
        return True
    
    def validate_target_position(self):
        """Valida que la posición objetivo sea válida"""
        return self.target_position is not None