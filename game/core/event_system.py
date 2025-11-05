"""
Sistema de eventos global para desacoplar componentes del juego
"""
import inspect
from typing import Dict, List, Callable, Any

class EventSystem:
    """
    Sistema de publicación-suscripción para comunicación entre sistemas
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._event_history: List[Dict] = []
        self.max_history = 100  # Límite de eventos en historial
    
    def subscribe(self, event_type: str, callback: Callable):
        """Suscribe una función a un tipo de evento"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            print(f"🔔 {callback.__name__} suscrito a {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Desuscribe una función de un tipo de evento"""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            print(f"🔕 {callback.__name__} desuscrito de {event_type}")
    
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """Emite un evento a todos los suscriptores"""
        if data is None:
            data = {}
        
        # Registrar evento en historial
        event_record = {
            'type': event_type,
            'data': data,
            'timestamp': len(self._event_history)
        }
        self._event_history.append(event_record)
        
        # Mantener historial limitado
        if len(self._event_history) > self.max_history:
            self._event_history.pop(0)
        
        print(f"🎯 EVENTO EMITIDO: {event_type}")
        
        # Notificar a suscriptores
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    # Pasar datos según lo que la callback espera
                    sig = inspect.signature(callback)
                    if len(sig.parameters) == 0:
                        callback()
                    else:
                        callback(data)
                except Exception as e:
                    print(f"❌ Error en callback {callback.__name__} para evento {event_type}: {e}")
    
    def get_event_history(self, event_type: str = None):
        """Obtiene el historial de eventos"""
        if event_type:
            return [e for e in self._event_history if e['type'] == event_type]
        return self._event_history
    
    def clear_listeners(self):
        """Limpia todos los suscriptores"""
        self._listeners.clear()
        print("🧹 Todos los listeners limpiados")

    # 🎯 NUEVO: Alias para compatibilidad con register/subscribe
    def register(self, event_type: str, callback: Callable):
        """Alias de subscribe para compatibilidad"""
        self.subscribe(event_type, callback)


# Instancia global del sistema de eventos
event_system = EventSystem()


# Definición de tipos de eventos
class EventTypes:
    """Tipos de eventos estándar del juego"""
    
    # Sistema de combate
    ENTITY_DAMAGED = "entity_damaged"
    ENTITY_HEALED = "entity_healed"
    ENTITY_DIED = "entity_died"
    ENTITY_KILLED = "entity_killed"  # 🎯 NUEVO: Para cuando una entidad mata a otra
    ENTITY_LEVEL_UP = "entity_level_up"
    
    # Sistema de turnos
    TURN_STARTED = "turn_started"
    TURN_ENDED = "turn_ended"
    TURN_PHASE_CHANGED = "turn_phase_changed"
    
    # Sistema de habilidades
    ABILITY_USED = "ability_used"
    ABILITY_SELECTED = "ability_selected"
    ABILITY_CANCELLED = "ability_cancelled"
    ABILITY_SELECTION_ENDED = "ability_selection_ended"  # 🎯 NUEVO: Para el sistema de estados
    
    # Sistema de movimiento
    ENTITY_MOVED = "entity_moved"
    DASH_DAMAGE_APPLIED = "dash_damage_applied"
    
    # Sistema de recursos
    PH_CHANGED = "ph_changed"
    HP_CHANGED = "hp_changed"
    ENERGY_CHANGED = "energy_changed"  # 🎯 NUEVO: Para el sistema de energía
    
    # Sistema de UI
    ENTITY_SELECTED = "entity_selected"
    ENTITY_DESELECTED = "entity_deselected"
    MENU_OPENED = "menu_opened"
    MENU_CLOSED = "menu_closed"
    
    # Sistema de progresión
    EXPERIENCE_GAINED = "experience_gained"
    LEVEL_COMPLETED = "level_completed"
    GAME_OVER = "game_over"
    VICTORY = "victory"

    # Sistema de efectos y estados
    EFFECT_APPLIED = "effect_applied"
    EFFECT_REMOVED = "effect_removed"
    EFFECT_EXPIRED = "effect_expired"
    PASSIVE_TRIGGERED = "passive_triggered"


# Decoradores útiles para suscribir funciones
def event_listener(event_type: str):
    """Decorador para marcar funciones como listeners de eventos"""
    def decorator(func: Callable):
        event_system.subscribe(event_type, func)
        return func
    return decorator