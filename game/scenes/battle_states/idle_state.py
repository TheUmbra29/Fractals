# game/scenes/battle_states/idle_state.py
from .base_state import BattleState
import pygame

class IdleState(BattleState):
    """Estado por defecto - selección de personajes y acciones básicas"""
    
    def enter(self):
        print("🔄 Entrando a estado: Idle")
    
    def exit(self):
        print("🔄 Saliendo de estado: Idle")
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
    
    def _handle_click(self, pos):
        """Maneja clics en estado idle"""
        grid_pos = self.battle_scene.grid.get_grid_position(pos)
        if not self.battle_scene.grid.is_valid_position(grid_pos):
            return
        
        # Selección de aliado
        for entity in self.battle_scene.entities:
            if (entity.position == grid_pos and 
                self.battle_scene.turn_system.can_select(entity)):
                self.battle_scene.selected_entity = entity
                print(f"✅ {entity.name} seleccionado")
                return
        
        # Si hay personaje seleccionado, ataque básico a enemigos
        if self.battle_scene.selected_entity:
            enemy = next((e for e in self.battle_scene.entities 
                         if e.position == grid_pos and e.team == "enemy"), None)
            if enemy and not self.battle_scene.selected_entity.has_acted:
                self.battle_scene.selected_entity.basic_attack(enemy)
    
    def _handle_keydown(self, event):
        if event.key == pygame.K_SPACE:
            self.battle_scene.end_turn()
        elif event.key == pygame.K_ESCAPE:
            self.battle_scene.clear_selections()
        elif event.key == pygame.K_h and self.battle_scene.selected_entity:
            self.battle_scene.open_ability_menu()
        elif event.key == pygame.K_m and self.battle_scene.selected_entity:
            self.battle_scene.set_state("movement")
        elif event.key == pygame.K_p:  # 🆕 NUEVO: Tecla P para menú de pausa
            self.battle_scene.open_menu("pause")
        elif event.key == pygame.K_i:  # 🆕 NUEVO: Tecla I para inventario
            self.battle_scene.open_menu("inventory")
    
    def update(self):
        """No hay actualizaciones específicas en idle"""
        pass
    
    def draw(self):
        """No hay elementos específicos para dibujar en idle"""
        pass
    
    def get_instructions(self):
        if self.battle_scene.selected_entity:
            return [
                "M: Movimiento", 
                "H: Habilidades", 
                "P: Menú pausa",
                "I: Inventario",
                "CLIC en enemigo: Atacar",
                "ESPACIO: Terminar turno"
            ]
        return [
            "Selecciona un personaje", 
            "P: Menú pausa",
            "ESPACIO: Terminar turno"
        ]