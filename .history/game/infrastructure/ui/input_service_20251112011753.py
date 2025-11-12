 
import pygame
from typing import Optional, Tuple

class InputService:
    
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.keys_pressed = set()
    
    def process_events(self):
        self.mouse_clicked = False
        self.keys_pressed.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keys_pressed.add("QUIT")
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
 
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_clicked = True
 
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
    
    def _handle_keydown(self, event):
        key_map = {
            pygame.K_ESCAPE: "ESCAPE",
            pygame.K_SPACE: "SPACE", 
            pygame.K_r: "RESET",
            pygame.K_1: "ABILITY_1",
            pygame.K_2: "ABILITY_2",
            pygame.K_RETURN: "ENTER",
            pygame.K_h: "H",  # Agrega la tecla H para menú de habilidades
        }
        
        if event.key in key_map:
            self.keys_pressed.add(key_map[event.key])
    
    def get_mouse_grid_position(self, grid_offset: Tuple[int, int], cell_size: int, grid_size: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        screen_x, screen_y = self.mouse_pos
        grid_x = (screen_x - grid_offset[0]) // cell_size
        grid_y = (screen_y - grid_offset[1]) // cell_size
        
 
        if (0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1]):
            return (grid_x, grid_y)
        return None
    
    def is_key_pressed(self, key: str) -> bool:
        return key in self.keys_pressed
    
    def is_mouse_clicked(self) -> bool:
        return self.mouse_clicked
    
    def get_mouse_position(self) -> Tuple[int, int]:
        return self.mouse_pos
    
    def get_mouse_grid_position(self, grid_offset: Tuple[int, int], cell_size: int, grid_size: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        screen_x, screen_y = self.mouse_pos
        grid_x = (screen_x - grid_offset[0]) // cell_size
        grid_y = (screen_y - grid_offset[1]) // cell_size
        
 
        if (0 <= grid_x < grid_size[0] and 0 <= grid_y < grid_size[1]):
            return (grid_x, grid_y)
        return None