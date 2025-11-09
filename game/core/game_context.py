"""
GameContext - Contenedor central de dependencias  
SINGLE SOURCE OF TRUTH para todos los sistemas
"""
from typing import Dict, Any, Optional
from game.core.event_system import event_system
from game.core.config_manager import ConfigManager
from game.core.action_base import ActionContext
from game.core.logger import logger

class GameContext:
    """Contenedor central de dependencias - SINGLE SOURCE OF TRUTH"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GameContext()
        return cls._instance
    
    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.event_system = event_system
        self.config_manager = ConfigManager.get_instance()
        self._initialized = False
        logger.debug("GameContext creado")
    
    def initialize(self):
        """Inicializa todos los sistemas en ORDEN CORRECTO"""
        if self._initialized:
            return
            
        logger.info("🔄 Inicializando GameContext...")
        
        # FASE 1: Sistemas base (sin dependencias)
        from game.systems.grid_system import GridSystem
        from game.systems.turn_system import TurnSystem
        from game.systems.movement_system import MovementSystem
        
        self.register_system('grid', GridSystem())
        self.register_system('turn', TurnSystem())
        self.register_system('movement', MovementSystem(self.get_system('grid')))
        
        # FASE 2: Sistemas de datos/efectos
        from game.systems.effect_system import EffectSystem
        from game.systems.passive_system import PassiveSystem
        
        self.register_system('effect', EffectSystem())
        self.register_system('passive', PassiveSystem())
        
        # FASE 3: Sistemas complejos (con todas sus dependencias)
        from game.systems.ability_system import AbilitySystem
        
        self.register_system('ability', AbilitySystem(
            self.get_system('grid'),
            self.get_system('effect'),
            self  # ✅ Inyectar el contexto
        ))
        
        # Cargar configuración de efectos
        from game.data.effects import EFFECTS_CONFIG
        self.get_system('effect').load_effects_config(EFFECTS_CONFIG)
        
        self._initialized = True
        logger.info("✅ GameContext inicializado completamente")
    
    def register_system(self, system_name: str, system_instance: Any):
        """Registra un sistema en el contexto"""
        if system_name in self.systems:
            logger.warning(f"Sistema {system_name} ya registrado, sobreescribiendo")
        
        self.systems[system_name] = system_instance
        logger.debug(f"📋 Sistema registrado: {system_name}")
    
    def get_system(self, system_name: str) -> Optional[Any]:
        """Obtiene un sistema del contexto"""
        system = self.systems.get(system_name)
        if not system:
            logger.warning(f"⚠️ Sistema no encontrado: {system_name}")
        return system
    
    def create_ability_context(self, caster, target=None, target_position=None, entities=None):
        """Crea contexto de habilidad CON todas las dependencias inyectadas"""
        context = ActionContext(
            caster=caster,
            target=target,
            target_position=target_position,
            entities=entities or []
        )
        
        # ✅ INYECTAR TODAS LAS DEPENDENCIAS NECESARIAS
        context.extra_data = {
            'effect_system': self.get_system('effect'),
            'game_context': self,
            'event_system': self.event_system,
            'turn_system': self.get_system('turn')
        }
        
        return context

# Instancia global del contexto
game_context = GameContext()