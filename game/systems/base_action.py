"""
Sistema base de acciones - Reemplazo definitivo para action_system obsoleto.
Diseñado para escalabilidad y mantenibilidad a largo plazo.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from game.core.event_system import event_system, EventTypes


class ActionContext:
    """Contexto unificado para ejecución de acciones - VERSIÓN MEJORADA"""
    
    def __init__(self, 
                 caster, 
                 target=None, 
                 target_position: Optional[Tuple[int, int]] = None,
                 entities: Optional[List] = None,
                 ability_name: str = "",
                 **kwargs):
        self.caster = caster
        self.target = target
        self.target_position = target_position
        self.entities = entities or []
        self.ability_name = ability_name
        self.extra_data = kwargs  # Datos extensibles para futuro crecimiento
    
    def validate_target(self, required_team: Optional[str] = None) -> bool:
        """Valida que el target cumpla con los requisitos"""
        if not self.target:
            return False
        
        if required_team and self.target.team != required_team:
            return False
            
        return True
    
    def validate_target_position(self) -> bool:
        """Valida que la posición objetivo sea válida"""
        return self.target_position is not None
    
    def get_entity_at_position(self, position: Tuple[int, int]):
        """Obtiene entidad en una posición específica"""
        return next((e for e in self.entities if e.position == position), None)


class BaseAction(ABC):
    """
    Clase base abstracta para TODAS las acciones del juego.
    Diseñada para ser extensible y mantenible.
    """
    
    def __init__(self, 
                 name: str, 
                 action_type: str, 
                 cost_ph: int = 0, 
                 cooldown: int = 0,
                 selection_mode: str = "enemy",
                 range: int = 1):
        self.name = name
        self.type = action_type
        self.cost_ph = cost_ph
        self.cooldown = cooldown
        self.selection_mode = selection_mode
        self.range = range
        self.current_cooldown = 0
    
    def can_execute(self, context: ActionContext) -> bool:
        """
        Valida si la acción puede ejecutarse.
        Método final que implementa validaciones base.
        """
        # Validación de PH
        if context.caster.stats['current_ph'] < self.cost_ph:
            return False
        
        # Validación de cooldown
        if self.current_cooldown > 0:
            return False
        
        # Validaciones específicas por tipo
        if not self._validate_specific_conditions(context):
            return False
            
        return True
    
    def _validate_specific_conditions(self, context: ActionContext) -> bool:
        """Validaciones específicas que las subclases pueden override"""
        if self.type == 'movement' and context.caster.has_moved:
            return False
            
        if self.type == 'ability' and context.caster.has_acted:
            return False
            
        return True
    
    def execute(self, context: ActionContext) -> bool:
        """
        Ejecuta la acción con manejo completo de errores.
        Retorna True si la ejecución fue exitosa.
        """
        if not self.can_execute(context):
            return False
        
        try:
            # Pre-ejecución
            self._on_before_execute(context)
            
            # Ejecución principal
            success = self._execute_impl(context)
            
            # Post-ejecución
            if success:
                self._on_success(context)
            else:
                self._on_failure(context)
                
            return success
            
        except Exception as e:
            self._on_error(context, e)
            return False
    
    @abstractmethod
    def _execute_impl(self, context: ActionContext) -> bool:
        """Implementación específica de la acción - DEBE ser implementado por subclases"""
        pass
    
    def _on_before_execute(self, context: ActionContext):
        """Hook llamado antes de la ejecución"""
        pass
    
    def _on_success(self, context: ActionContext):
        """Hook llamado después de ejecución exitosa"""
        # Consumir PH
        context.caster.stats['current_ph'] -= self.cost_ph
        
        # Iniciar cooldown si es necesario
        if self.cooldown > 0:
            self.start_cooldown()
        
        # Emitir evento
        event_system.emit(EventTypes.ABILITY_USED, {
            'caster': context.caster,
            'ability': self.name,
            'context': context
        })
    
    def _on_failure(self, context: ActionContext):
        """Hook llamado después de ejecución fallida"""
        print(f"❌ {self.name} falló al ejecutarse")
    
    def _on_error(self, context: ActionContext, error: Exception):
        """Hook llamado cuando ocurre un error"""
        print(f"💥 Error en {self.name}: {error}")
    
    def start_cooldown(self):
        """Inicia el cooldown de la acción"""
        self.current_cooldown = self.cooldown
    
    def update_cooldown(self):
        """Actualiza el cooldown (llamar cada turno)"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def get_description(self) -> str:
        """Descripción para la UI - puede ser override por subclases"""
        return f"{self.name} - Costo: {self.cost_ph} PH - Rango: {self.range}"
    
    def get_range(self) -> int:
        """Rango de la acción"""
        return self.range
    
    def get_selection_mode(self) -> str:
        """Modo de selección para el sistema de UI"""
        return self.selection_mode