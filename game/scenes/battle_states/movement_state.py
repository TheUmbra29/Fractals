# game/scenes/battle_states/movement_state.py
from .base_state import BattleState
import pygame

class MovementState(BattleState):
    """Estado para manejar movimiento de personajes"""
    
    def enter(self):
        print("🎯 Entrando a estado: Movement")
        if self.battle_scene.selected_entity:
            success = self.battle_scene.movement_system.start_movement(
                self.battle_scene.selected_entity, 
                self.battle_scene.entities
            )
            if not success:
                # Si no se puede mover, volver a idle
                self.battle_scene.set_state("idle")
    
    def exit(self):
        print("🎯 Saliendo de estado: Movement")
        self.battle_scene.movement_system.cancel()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
    
    def _handle_click(self, pos):
        """Maneja clics para movimiento"""
        grid_pos = self.battle_scene.grid.get_grid_position(pos)
        if self.battle_scene.grid.is_valid_position(grid_pos):
            self.battle_scene.movement_system.handle_click(
                grid_pos, 
                self.battle_scene.entities
            )
    
    def _handle_keydown(self, event):
        """Maneja teclas en estado movimiento"""
        if event.key == pygame.K_RETURN:
            if self.battle_scene.movement_system.execute_movement():
                self.battle_scene.set_state("idle")
        elif event.key == pygame.K_ESCAPE:
            self.battle_scene.set_state("idle")
    
    def update(self):
        """Actualiza previsualización de movimiento"""
        self.battle_scene.movement_system.update_preview(
            pygame.mouse.get_pos(),
            self.battle_scene.entities
        )
    
    def draw(self):
        """Dibuja la ruta de movimiento"""
        self.battle_scene.movement_system.draw(self.battle_scene.screen)
    
    def get_instructions(self):
        """Instrucciones para movimiento"""
        state_info = self.battle_scene.movement_system.get_state_info()
        base_instructions = [
            "MODO MOVIMIENTO ACTIVO",
            "CLIC en enemigo: Marcar embestida", 
            "CLIC en vacío: Mover/Retroceder",
            "ENTER: Confirmar movimiento",
            "ESC: Cancelar movimiento"
        ]
        
        if state_info['dash_targets'] > 0:
            base_instructions.append(f"🎯 Enemigos marcados: {state_info['dash_targets']}")
        
        return base_instructions