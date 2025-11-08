"""
Sistema de logging centralizado para manejo de errores
"""
import traceback
from datetime import datetime
import os

class GameLogger:
    def __init__(self, log_to_file=True):
        self.error_count = 0
        self.warning_count = 0
        self.log_to_file = log_to_file
        self.log_file = "game_log.txt"
        
        # Crear directorio de logs si no existe
        if log_to_file:
            self._ensure_log_directory()
            self._clear_old_logs()
    
    def _ensure_log_directory(self):
        """Asegura que el directorio de logs exista"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = os.path.join(log_dir, "game_log.txt")
    
    def _clear_old_logs(self):
        """Limpia logs muy antiguos (opcional)"""
        try:
            # Mantener solo los últimos 5 logs
            log_dir = "logs"
            if os.path.exists(log_dir):
                logs = [f for f in os.listdir(log_dir) if f.startswith("game_log")]
                if len(logs) > 5:
                    # Ordenar por fecha de modificación y eliminar los más viejos
                    logs.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))
                    for old_log in logs[:-5]:
                        os.remove(os.path.join(log_dir, old_log))
        except Exception as e:
            print(f"⚠️ No se pudieron limpiar logs antiguos: {e}")
    
    def _write_to_file(self, level, message):
        """Escribe el log en archivo"""
        if not self.log_to_file:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            print(f"❌ Error escribiendo en log file: {e}")
    
    def error(self, message, exception=None, context=None):
        """Log de errores críticos"""
        self.error_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_message = f"❌ [{timestamp}] ERROR: {message}"
        if context:
            log_message += f" | Contexto: {context}"
        
        print(log_message)
        
        if exception:
            print(f"    Exception: {exception}")
            traceback.print_exc()
            # Guardar traceback completo en archivo
            if self.log_to_file:
                tb_str = traceback.format_exc()
                self._write_to_file("ERROR", f"{message} | Exception: {exception}\n{tb_str}")
        else:
            self._write_to_file("ERROR", message)
    
    def warning(self, message, context=None):
        """Log de advertencias"""
        self.warning_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_message = f"⚠️ [{timestamp}] WARNING: {message}"
        if context:
            log_message += f" | Contexto: {context}"
        
        print(log_message)
        self._write_to_file("WARNING", message)
    
    def info(self, message, context=None):
        """Log informativo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_message = f"ℹ️ [{timestamp}] INFO: {message}"
        if context:
            log_message += f" | Contexto: {context}"
        
        print(log_message)
        self._write_to_file("INFO", message)
    
    def debug(self, message, context=None):
        """Log de depuración"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_message = f"🐛 [{timestamp}] DEBUG: {message}"
        if context:
            log_message += f" | Contexto: {context}"
        
        print(log_message)
        self._write_to_file("DEBUG", message)
    
    def ability_used(self, caster, ability_name, target=None, success=True):
        """Log especializado para uso de habilidades"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅" if success else "❌"
        
        message = f"{status} [{timestamp}] ABILITY: {caster.name} -> {ability_name}"
        if target:
            message += f" -> {target.name}"
        
        print(message)
        self._write_to_file("ABILITY", message)
    
    def combat_event(self, event_type, attacker=None, target=None, damage=0, healing=0):
        """Log especializado para eventos de combate"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"⚔️ [{timestamp}] COMBAT: {event_type}"
        if attacker:
            message += f" | Atacante: {attacker.name}"
        if target:
            message += f" | Objetivo: {target.name}"
        if damage > 0:
            message += f" | Daño: {damage}"
        if healing > 0:
            message += f" | Curación: {healing}"
        
        print(message)
        self._write_to_file("COMBAT", message)
    
    def state_change(self, from_state, to_state, entity=None):
        """Log especializado para cambios de estado"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        message = f"🔄 [{timestamp}] STATE: {from_state} → {to_state}"
        if entity:
            message += f" | Entidad: {entity.name}"
        
        print(message)
        self._write_to_file("STATE", message)
    
    def get_stats(self):
        """Obtiene estadísticas del logging"""
        return {
            "errors": self.error_count,
            "warnings": self.warning_count,
            "log_file": self.log_file if self.log_to_file else "No file logging"
        }
    
    def reset_stats(self):
        """Reinicia las estadísticas de logging"""
        self.error_count = 0
        self.warning_count = 0

logger = GameLogger(log_to_file=True)

def debug_quick(msg, value=None):
    """Función rápida para debug"""
    if value is not None:
        logger.debug(f"{msg}: {value}")
    else:
        logger.debug(msg)