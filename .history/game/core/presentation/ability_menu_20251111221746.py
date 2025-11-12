import pygame
from typing import List
from core.domain.entities.battle_entity import BattleEntity

class AbilityMenu:
    def __init__(self, entity: BattleEntity, position: tuple):
        self.entity = entity
        self.position = position
        self.abilities = entity.habilidades
        self.selected_index = 0
        self.visible = True
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw(self, screen):
        if not self.visible or not self.abilities:
            return
        x, y = self.position
        width = 250
        item_height = 60
        height = len(self.abilities) * item_height + 10
        # Fondo del menú
        pygame.draw.rect(screen, (40, 40, 60), (x, y, width, height))
        pygame.draw.rect(screen, (100, 100, 200), (x, y, width, height), 2)
        # Título
        title_text = f"Habilidades de {self.entity.name}"
        title_surface = self.font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (x + 10, y + 5))
        # Línea separadora
        pygame.draw.line(screen, (100, 100, 200), (x, y + 35), (x + width, y + 35), 1)
        # Lista de habilidades
        for i, ability in enumerate(self.abilities):
            item_y = y + 40 + i * item_height
            # Fondo del ítem
            if i == self.selected_index:
                pygame.draw.rect(screen, (60, 60, 100), (x, item_y, width, item_height))
            # Nombre y costo
            color = (200, 200, 255) if ability.puede_usar(self.entity) else (100, 100, 100)
            name_text = f"{ability.nombre} (PH: {ability.costo_ph})"
            name_surface = self.font.render(name_text, True, color)
            screen.blit(name_surface, (x + 10, item_y + 5))
            # Descripción
            desc_surface = self.small_font.render(ability.descripcion, True, (180, 180, 180))
            screen.blit(desc_surface, (x + 10, item_y + 25))
            # Estado TdE
            if ability.td_e_actual > 0:
                cd_text = f"TdE: {ability.td_e_actual}"
                cd_surface = self.small_font.render(cd_text, True, (255, 100, 100))
                screen.blit(cd_surface, (x + width - 60, item_y + 5))
            else:
                ready_text = "LISTA"
                ready_surface = self.small_font.render(ready_text, True, (100, 255, 100))
                screen.blit(ready_surface, (x + width - 60, item_y + 5))
    
    def handle_input(self, event):
        if not self.visible:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.abilities) - 1, self.selected_index + 1)
            elif event.key == pygame.K_RETURN:
                selected_ability = self.abilities[self.selected_index]
                if selected_ability.puede_usar(self.entity):
                    return selected_ability.id
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
        return None
    
    def get_selected_ability(self):
        if self.abilities and 0 <= self.selected_index < len(self.abilities):
            return self.abilities[self.selected_index]
        return None
