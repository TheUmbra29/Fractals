import pygame
from typing import List, Callable, Optional
from core.domain.entities.battle_entity import BattleEntity

class ActionMenu:
    def __init__(self, entity: BattleEntity, screen_position: tuple):
        self.entity = entity
        self.screen_position = screen_position
        self.visible = True
        self.buttons = []
        
        self.actions = self._build_available_actions()
    
    def _build_available_actions(self) -> List[dict]:
        actions = [
            {
                "name": "Moverse", 
                "key": "M", 
                "type": "move",
                "enabled": self._can_move(),
                "description": "Trazar ruta y mover entidad",
                "ph_cost": 0,
                "cooldown": 0
            },
            {
                "name": "Atacar", 
                "key": "A", 
                "type": "attack_menu",
                "enabled": True,
                "description": "Desplegar menú de habilidades",
                "ph_cost": 0,
                "cooldown": 0
            }
        ]
        return actions
    
    def _get_ability_key(self, ability_type: str) -> str:
        key_map = {
            "basic_attack": "A",
            "ability_alpha": "1", 
            "ability_beta": "2",
            "ability_ultimate": "3"
        }
        return key_map.get(ability_type, "?")
    
    def _can_move(self) -> bool:
        return not self.entity.has_moved
    
    def _can_attack(self) -> bool:
        return "basic_attack" not in self.entity.actions_used_this_turn
    
    def _can_use_ability(self, ability_type: str) -> bool:
        return ability_type not in self.entity.actions_used_this_turn
    
    def handle_click(self, mouse_pos: tuple) -> Optional[str]:
        for button in self.buttons:
            if button["rect"].collidepoint(mouse_pos):
                return button["action_type"]
        return None
    
    def draw(self, screen: pygame.Surface):
        if not self.visible or not self.actions:
            return
        
        menu_width = 280  # Más ancho para mostrar PH/TdE
        item_height = 50  # Más alto para información adicional
        padding = 10
        menu_height = len(self.actions) * item_height + padding * 2
        
        x, y = self.screen_position
        
        if x + menu_width > screen.get_width():
            x = screen.get_width() - menu_width - 10
        if y + menu_height > screen.get_height():
            y = screen.get_height() - menu_height - 10
        
        menu_rect = pygame.Rect(x, y, menu_width, menu_height)
        pygame.draw.rect(screen, (40, 40, 60), menu_rect)
        pygame.draw.rect(screen, (100, 100, 150), menu_rect, 2)
        
        header_rect = pygame.Rect(x, y, menu_width, 30)
        pygame.draw.rect(screen, (60, 60, 80), header_rect)
        
        ph_font = pygame.font.Font(None, 20)
        ph_text = f"PH: {self.entity.current_ph}/{self.entity.max_ph}"
        ph_surface = ph_font.render(ph_text, True, (200, 200, 255))
        screen.blit(ph_surface, (x + 10, y + 8))
        
        self.buttons = []
        font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 16)
        
        for i, action in enumerate(self.actions):
            button_y = y + 30 + i * item_height
            button_rect = pygame.Rect(
                x + padding, 
                button_y, 
                menu_width - padding * 2, 
                item_height - 5
            )
            
            self.buttons.append({
                "rect": button_rect,
                "action_type": action["type"]
            })
            
            if action["enabled"]:
                color = (80, 120, 200)
                border_color = (120, 160, 220)
                text_color = (255, 255, 255)
            else:
                color = (60, 60, 80)
                border_color = (80, 80, 100)
                text_color = (150, 150, 150)
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, 2)
            
            action_text = f"{action['name']} ({action['key']})"
            text_surface = font.render(action_text, True, text_color)
            screen.blit(text_surface, (button_rect.x + 10, button_rect.y + 5))
            
            info_text = f"Costo: {action['ph_cost']} PH"
            if action["cooldown"] > 0:
                info_text += f" | TdE: {action['cooldown']}"
            
            info_surface = small_font.render(info_text, True, (200, 200, 200))
            screen.blit(info_surface, (button_rect.x + 10, button_rect.y + 25))
            
            desc_surface = small_font.render(action['description'], True, (180, 180, 180))
            screen.blit(desc_surface, (button_rect.x + 10, button_rect.y + 35))            

    def set_visibility(self, visible: bool):
        self.visible = visible