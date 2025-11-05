# game/scenes/battle_states/targeting_state.py
import pygame
from .base_state import BattleState

class TargetingState(BattleState):
    """Estado para selección avanzada de objetivos (cono, línea, área)"""
    
    def __init__(self, battle_scene, ability_data, targeting_type="area"):
        super().__init__(battle_scene)
        self.ability_data = ability_data
        self.targeting_type = targeting_type
        self.valid_positions = []
        self.current_position = None
    
    def enter(self):
        print(f"🎯 Entrando a estado: Targeting ({self.targeting_type})")
        self._calculate_valid_positions()
    
    def exit(self):
        print("🎯 Saliendo de estado: Targeting")
        self.valid_positions = []
    
    def _calculate_valid_positions(self):
        """Calcula posiciones válidas según el tipo de targeting"""
        caster_pos = self.battle_scene.selected_entity.position
        range_val = self.ability_data.get('range', 1)
        
        self.valid_positions = []
        
        for x in range(caster_pos[0] - range_val, caster_pos[0] + range_val + 1):
            for y in range(caster_pos[1] - range_val, caster_pos[1] + range_val + 1):
                pos = (x, y)
                distance = abs(x - caster_pos[0]) + abs(y - caster_pos[1])
                
                if (self.battle_scene.grid.is_valid_position(pos) and 
                    distance <= range_val and 
                    pos != caster_pos):
                    
                    self.valid_positions.append(pos)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._update_cursor_position(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.battle_scene.set_state("idle")
    
    def _update_cursor_position(self, pos):
        """Actualiza la posición del cursor para previsualización"""
        grid_pos = self.battle_scene.grid.get_grid_position(pos)
        if grid_pos in self.valid_positions:
            self.current_position = grid_pos
        else:
            self.current_position = None
    
    def _handle_click(self, pos):
        """Maneja clic para confirmar selección"""
        grid_pos = self.battle_scene.grid.get_grid_position(pos)
        
        if grid_pos in self.valid_positions:
            print(f"🎯 Objetivo seleccionado: {grid_pos}")
            # Aquí ejecutaríamos la habilidad con el objetivo
            self.battle_scene.set_state("idle")
    
    def update(self):
        """No hay actualizaciones continuas"""
        pass
    
    def draw(self):
        """Dibuja el área de targeting"""
        screen = self.battle_scene.screen
        
        # Dibujar posiciones válidas
        for pos in self.valid_positions:
            screen_pos = self.battle_scene.grid.get_screen_position(pos)
            rect = pygame.Rect(screen_pos[0], screen_pos[1], 
                             self.battle_scene.grid.cell_size, 
                             self.battle_scene.grid.cell_size)
            
            highlight = pygame.Surface((self.battle_scene.grid.cell_size, 
                                      self.battle_scene.grid.cell_size), 
                                      pygame.SRCALPHA)
            highlight.fill((255, 200, 50, 120))
            screen.blit(highlight, rect)
            pygame.draw.rect(screen, (255, 150, 50), rect, 2)
        
        # Dibujar previsualización en posición actual
        if self.current_position:
            screen_pos = self.battle_scene.grid.get_screen_position(self.current_position)
            center_x = screen_pos[0] + self.battle_scene.grid.cell_size // 2
            center_y = screen_pos[1] + self.battle_scene.grid.cell_size // 2
            
            # Círculo de confirmación
            pygame.draw.circle(screen, (255, 100, 100), (center_x, center_y), 15, 3)
    
    def get_instructions(self):
        return ["CLIC: Seleccionar objetivo", "ESC: Cancelar"]