"""
Estado global persistente del juego entre escenas
"""
from typing import List, Dict, Any
from .event_system import event_system, EventTypes

class GameState:
    """Mantiene el estado persistente del juego"""
    
    def __init__(self):
        # Equipo del jugador
        self.player_team: List[str] = ["Ricchard"]  # Nombres de personajes desbloqueados
        self.current_party: List[str] = ["Ricchard"]  # Personajes en el equipo actual
        
        # Progresión
        self.current_level: int = 1
        self.completed_levels: List[int] = []
        self.total_experience: int = 0
        self.game_difficulty: str = "normal"  # "easy", "normal", "hard"
        
        # Recursos globales
        self.player_resources: Dict[str, int] = {
            "gold": 0,
            "premium_currency": 0
        }
        
        # Estadísticas
        self.game_statistics: Dict[str, Any] = {
            "enemies_defeated": 0,
            "abilities_used": 0,
            "total_damage_dealt": 0,
            "total_healing_done": 0,
            "turns_played": 0
        }
        
        # Configuración
        self.settings: Dict[str, Any] = {
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "show_tutorial": True,
            "auto_end_turn": False
        }
        
        # Suscribir a eventos para actualizar estadísticas
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Configura listeners para actualizar estadísticas automáticamente"""
        event_system.subscribe(EventTypes.ENTITY_DIED, self._on_entity_died)
        event_system.subscribe(EventTypes.ABILITY_USED, self._on_ability_used)
        event_system.subscribe(EventTypes.ENTITY_DAMAGED, self._on_entity_damaged)
        event_system.subscribe(EventTypes.TURN_ENDED, self._on_turn_ended)
    
    def _on_entity_died(self, data):
        """Actualiza estadísticas cuando una entidad muere"""
        if data.get('entity') and data['entity'].team == "enemy":
            self.game_statistics["enemies_defeated"] += 1
    
    def _on_ability_used(self, data):
        """Actualiza estadísticas cuando se usa una habilidad"""
        self.game_statistics["abilities_used"] += 1
    
    def _on_entity_damaged(self, data):
        """Actualiza estadísticas de daño"""
        damage = data.get('damage', 0)
        if damage > 0:
            self.game_statistics["total_damage_dealt"] += damage
    
    def _on_turn_ended(self, data):
        """Actualiza estadísticas de turnos"""
        self.game_statistics["turns_played"] += 1
    
    def unlock_character(self, character_name: str):
        """Desbloquea un nuevo personaje"""
        if character_name not in self.player_team:
            self.player_team.append(character_name)
            print(f"🎉 Personaje desbloqueado: {character_name}")
    
    def add_to_party(self, character_name: str):
        """Añade un personaje al equipo actual"""
        if character_name in self.player_team and character_name not in self.current_party:
            if len(self.current_party) < 3:  # Máximo 3 personajes
                self.current_party.append(character_name)
                print(f"👥 {character_name} añadido al equipo")
            else:
                print("❌ Equipo completo (máximo 3 personajes)")
    
    def complete_level(self, level_id: int, rating: int = 3):
        """Marca un nivel como completado"""
        if level_id not in self.completed_levels:
            self.completed_levels.append(level_id)
            
            # Recompensas por completar nivel
            exp_reward = level_id * 100
            gold_reward = level_id * 50
            
            self.total_experience += exp_reward
            self.player_resources["gold"] += gold_reward
            
            print(f"🏆 Nivel {level_id} completado!")
            print(f"💰 +{gold_reward} oro | ⭐ +{exp_reward} experiencia")
    
    def save_game(self):
        """Guarda el estado del juego (placeholder para implementación real)"""
        print("💾 Guardando partida...")
        # Aquí iría la lógica real de guardado
        return True
    
    def load_game(self):
        """Carga el estado del juego (placeholder)"""
        print("📂 Cargando partida...")
        # Aquí iría la lógica real de carga
        return True


# Instancia global del estado del juego
game_state = GameState()