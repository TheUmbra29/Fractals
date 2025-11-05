# game/scenes/battle_states/ability_state.py
from .base_state import BattleState
import pygame

class AbilityState(BattleState):
    """Estado para selección y uso de habilidades"""
    
    def enter(self):
        print("🔮 Entrando a estado: Ability")
    
    def exit(self):
        print("🔮 Saliendo de estado: Ability")
        self.battle_scene.ability_system.cancel_selection()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.battle_scene.set_state("idle")
    
    def _handle_click(self, pos):
        """Maneja clics para selección de habilidades"""
        grid_pos = self.battle_scene.grid.get_grid_position(pos)
        if self.battle_scene.grid.is_valid_position(grid_pos):
            success = self.battle_scene.ability_system.handle_click(
                grid_pos, 
                self.battle_scene.entities
            )
            if success:
                self.battle_scene.set_state("idle")
    
    def update(self):
        """No hay actualizaciones específicas"""
        pass
    
    def draw(self):
        """Dibuja indicadores de selección de habilidades"""
        self.battle_scene.ability_system.draw_target_indicators(self.battle_scene.screen)
    
    def get_instructions(self):
        """Instrucciones para selección de habilidades"""
        return ["CLIC: Seleccionar objetivo", "ESC: Cancelar habilidad"]