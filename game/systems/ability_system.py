"""
Sistema de habilidades - VERSIÓN REFACTORIZADA
"""
import pygame
from game.core.action_base import ActionContext  
from game.systems.selection_system import SelectionSystem
from game.core.logger import logger

class AbilitySystem:
    def __init__(self, grid_system, effect_system, game_context=None):
        self.grid_system = grid_system
        self.effect_system = effect_system
        self.game_context = game_context  # ✅ NUEVO: Contexto central
        self.selected_ability = None
        self.caster = None
        self.selection_system = SelectionSystem(self)
        logger.debug("AbilitySystem inicializado", {
            "grid_system": type(grid_system).__name__,
            "effect_system": "provided" if effect_system else "not provided",
            "game_context": "provided" if game_context else "not provided"
        })
    
    def set_effect_system(self, effect_system):
        """Setter para inyección de dependencias tardía"""
        self.effect_system = effect_system
    
    def select_ability(self, ability_data, caster, entities):
        if caster.has_acted:
            logger.warning(f"{caster.name} intentó usar habilidad pero ya actuó este turno")
            return False
        
        if caster.stats['current_ph'] < ability_data['cost_ph']:
            logger.warning(
                f"PH insuficiente para {ability_data['name']}", 
                {
                    "current_ph": caster.stats['current_ph'],
                    "required_ph": ability_data['cost_ph'],
                    "caster": caster.name
                }
            )
            return False
        
        self.selected_ability = ability_data
        self.caster = caster
        
        selection_mode = ability_data.get('selection_mode', 'enemy')
        success = self.selection_system.activate_mode(selection_mode, ability_data, caster, entities)
        
        if success:
            logger.info(
                f"Modo {selection_mode} activado para {ability_data['name']}",
                {"caster": caster.name, "ability": ability_data['name']}
            )
            return True
        else:
            logger.warning(
                f"No se pudo activar modo {selection_mode}",
                {"ability": ability_data['name'], "caster": caster.name}
            )
            self.clear_selection()
            return False
    
    def create_context(self, target_entity=None, target_position=None, entities=None):
        """Crea contexto MEJORADO - usa GameContext si está disponible"""
        # ✅ PRIORIDAD: Usar GameContext si está disponible
        if self.game_context:
            return self.game_context.create_ability_context(
                self.caster, target_entity, target_position, entities
            )
        
        # ✅ FALLBACK: Contexto legacy mejorado
        context = ActionContext(
            caster=self.caster,
            target=target_entity,
            target_position=target_position,
            entities=entities or []
        )
        
        # ✅ INYECCIÓN EXPLÍCITA (no más "adivinar")
        if not hasattr(context, 'extra_data'):
            context.extra_data = {}
        
        context.extra_data.update({
            'effect_system': self.effect_system,
            'game_context': self.game_context
        })
        
        return context
    
    def execute_ability_directly(self, context):
        """Ejecuta habilidad directamente - VERSIÓN CORREGIDA"""
        if not self.selected_ability or not self.caster:
            logger.warning("Intento de ejecutar habilidad sin selección previa")
            return False
        
        try:
            ability_key = self.selected_ability['key']
            if ability_key in self.caster.actions:
                # ✅ ASEGURAR EffectSystem en el contexto (solo si no viene del GameContext)
                if not hasattr(context, 'extra_data'):
                    context.extra_data = {}
                
                if 'effect_system' not in context.extra_data or context.extra_data['effect_system'] is None:
                    if self.effect_system:
                        context.extra_data['effect_system'] = self.effect_system
                    elif self.game_context:
                        context.extra_data['effect_system'] = self.game_context.get_system('effect')
                
                success = self.caster.perform_action(ability_key, context)

                if success:
                    logger.ability_used(
                        self.caster, 
                        self.selected_ability['name'], 
                        context.target,
                        success=True
                    )
                    self.clear_selection()
                    return True
                else:
                    logger.ability_used(
                        self.caster,
                        self.selected_ability['name'],
                        context.target, 
                        success=False
                    )
                    logger.warning(f"Habilidad {self.selected_ability['name']} falló al ejecutarse")
            else:
                logger.error(
                    f"Habilidad {ability_key} no encontrada en {self.caster.name}",
                    context={
                        "habilidades_disponibles": list(self.caster.actions.keys()),
                        "habilidad_solicitada": ability_key
                    }
                )
            
            return False
            
        except Exception as e:
            logger.error(
                f"Error crítico ejecutando habilidad {self.selected_ability['name']}",
                exception=e,
                context={
                    "caster": self.caster.name,
                    "ability": self.selected_ability,
                    "target": context.target.name if context.target else "None"
                }
            )
            return False
    
    def handle_click(self, grid_pos, entities):
        try:
            return self.selection_system.handle_click(grid_pos, entities)
        except Exception as e:
            logger.error(
                "Error manejando clic en AbilitySystem",
                exception=e,
                context={"grid_pos": grid_pos, "entities_count": len(entities)}
            )
            return False
    
    def draw_target_indicators(self, screen):
        try:
            self.selection_system.draw_indicators(screen)
        except Exception as e:
            logger.error("Error dibujando indicadores de objetivo", exception=e)
    
    def cancel_selection(self):
        try:
            return self.selection_system.cancel_selection()
        except Exception as e:
            logger.error("Error cancelando selección", exception=e)
            return False
    
    def clear_selection(self):
        try:
            self.selected_ability = None
            self.caster = None
            self.selection_system.cancel_selection()
            logger.debug("Selección de habilidad limpiada")
        except Exception as e:
            logger.error("Error limpiando selección", exception=e)
    
    def is_selecting(self):
        return self.selection_system.is_active()
    
    def get_selection_mode(self):
        return self.selection_system.get_current_mode_type()