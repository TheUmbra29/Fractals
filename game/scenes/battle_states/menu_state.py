# game/scenes/battle_states/menu_state.py
import pygame
from .base_state import BattleState

class MenuState(BattleState):
    """Estado para menús contextuales (pausa, inventario, opciones)"""
    
    def __init__(self, battle_scene, menu_type="pause"):
        super().__init__(battle_scene)
        self.menu_type = menu_type
        self.menu_options = self._get_menu_options()
        self.selected_index = 0
    
    def enter(self):
        print(f"📋 Entrando a estado: Menu ({self.menu_type})")
        self.selected_index = 0
    
    def exit(self):
        print(f"📋 Saliendo de estado: Menu")
    
    def _get_menu_options(self):
        """Define las opciones según el tipo de menú"""
        if self.menu_type == "pause":
            return ["Continuar", "Habilidades", "Objetos", "Opciones", "Salir"]
        elif self.menu_type == "inventory":
            return ["Usar objeto", "Equipar", "Examinar", "Volver"]
        return ["Volver"]
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.battle_scene.set_state("idle")
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self._select_option()
    
    def _select_option(self):
        """Ejecuta la opción seleccionada"""
        option = self.menu_options[self.selected_index]
        print(f"🎯 Seleccionado: {option}")
        
        if self.menu_type == "pause":
            if option == "Continuar":
                self.battle_scene.set_state("idle")
            elif option == "Habilidades":
                print("📊 Abriendo menú de habilidades extendido")
            elif option == "Salir":
                print("🚪 Saliendo del juego...")
                # Aquí iría la lógica para salir del juego
    
    def update(self):
        """No hay actualizaciones en menú estático"""
        pass
    
    def draw(self):
        """Dibuja el menú"""
        screen = self.battle_scene.screen
        width, height = screen.get_size()
        
        # Fondo semi-transparente
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Panel del menú
        menu_width, menu_height = 300, 250
        menu_x = (width - menu_width) // 2
        menu_y = (height - menu_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 60), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (100, 100, 200), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Título
        font_title = pygame.font.SysFont(None, 32)
        title = "MENÚ DE PAUSA" if self.menu_type == "pause" else "MENÚ"
        title_text = font_title.render(title, True, (255, 215, 0))
        screen.blit(title_text, (menu_x + (menu_width - title_text.get_width()) // 2, menu_y + 20))
        
        # Opciones
        font_option = pygame.font.SysFont(None, 28)
        for i, option in enumerate(self.menu_options):
            color = (255, 215, 0) if i == self.selected_index else (255, 255, 255)
            option_text = font_option.render(option, True, color)
            screen.blit(option_text, (menu_x + 50, menu_y + 70 + i * 40))
            
            # Indicador de selección
            if i == self.selected_index:
                pygame.draw.circle(screen, (255, 215, 0), 
                                 (menu_x + 30, menu_y + 85 + i * 40), 5)
    
    def get_instructions(self):
        return ["FLECHAS: Navegar", "ENTER: Seleccionar", "ESC: Volver"]