import pygame

class AbilityMenu:
    def __init__(self, screen, entity, position):
        self.screen = screen
        self.entity = entity
        self.position = position
        self.visible = False
        self.selected_index = 0
        self.abilities = self.get_entity_abilities()
    
    def get_entity_abilities(self):
        """🆕 CORREGIDO: Incluye selection_mode en cada habilidad"""
        abilities = []
        
        for action_key, action in self.entity.actions.items():
            if action_key == "move":
                continue
                
            abilities.append({
                "name": action.name,
                "key": action_key,
                "description": self.get_action_description(action),
                "cost_ph": action.cost_ph,
                "range": self.get_action_range(action),
                "type": action.type,
                "selection_mode": getattr(action, 'selection_mode', 'enemy')  # 🆕 NUEVO
            })
        
        print(f"📋 {self.entity.name} tiene {len(abilities)} habilidades: {[a['name'] for a in abilities]}")
        return abilities
    
    def get_action_description(self, action):
        """🆕 MEJORADO: Obtiene descripción con manejo de errores"""
        try:
            if hasattr(action, 'get_description'):
                return action.get_description()
            
            if hasattr(action, 'type'):
                if action.type == "attack":
                    return f"Ataque que causa daño - Costo: {getattr(action, 'cost_ph', 0)} PH"
                elif action.type == "support":
                    return f"Habilidad de soporte - Costo: {getattr(action, 'cost_ph', 0)} PH"
            
            return f"{getattr(action, 'name', 'Habilidad')} - Costo: {getattr(action, 'cost_ph', 0)} PH"
        
        except Exception as e:
            print(f"⚠️ Error obteniendo descripción: {e}")
            return f"{getattr(action, 'name', 'Habilidad')} - Costo: {getattr(action, 'cost_ph', 0)} PH"
    
    def get_action_range(self, action):
        """🆕 Obtiene rango REAL de la acción"""
        if hasattr(action, 'get_range'):
            return action.get_range()
        elif hasattr(action, 'range'):
            return action.range
        else:
            return 1  # Rango por defecto
    
    # El resto del código se mantiene igual...
    def draw(self):
        if not self.visible:
            return
            
        # 🆕 MEJORADO: Ajustar altura dinámicamente según número de habilidades
        menu_width = 350
        menu_height = 100 + len(self.abilities) * 40  # Altura dinámica
        menu_x = min(self.position[0], self.screen.get_width() - menu_width - 10)
        menu_y = max(10, self.position[1] - menu_height - 10)
        
        # Fondo con borde
        panel = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 230))
        self.screen.blit(panel, (menu_x, menu_y))
        pygame.draw.rect(self.screen, (255, 215, 0), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Fuentes
        font_title = pygame.font.SysFont('Arial', 24, bold=True)
        font_ability = pygame.font.SysFont('Arial', 20)
        font_desc = pygame.font.SysFont('Arial', 16)
        
        # Título
        title_text = font_title.render(f"HABILIDADES - {self.entity.name}", True, (255, 215, 0))
        self.screen.blit(title_text, (menu_x + 10, menu_y + 10))
        
        # Línea separadora
        pygame.draw.line(self.screen, (100, 100, 100), (menu_x + 10, menu_y + 45), 
                        (menu_x + menu_width - 10, menu_y + 45), 1)
        
        # Habilidades
        for i, ability in enumerate(self.abilities):
            y_pos = menu_y + 55 + i * 40
            
            # Fondo para habilidad seleccionada
            if i == self.selected_index:
                pygame.draw.rect(self.screen, (50, 50, 80), 
                               (menu_x + 5, y_pos - 5, menu_width - 10, 35))
            
            # Nombre y tecla
            color = (255, 215, 0) if i == self.selected_index else (255, 255, 255)
            ability_text = font_ability.render(f"[{i+1}] {ability['name']}", True, color)
            self.screen.blit(ability_text, (menu_x + 15, y_pos))
            
            # Stats de la habilidad
            stats_text = font_desc.render(f"PH: {ability['cost_ph']} | Rango: {ability['range']}", True, (150, 200, 255))
            self.screen.blit(stats_text, (menu_x + 200, y_pos))
            
            # Descripción (solo para la seleccionada)
            if i == self.selected_index:
                desc_text = font_desc.render(ability['description'], True, (200, 200, 200))
                self.screen.blit(desc_text, (menu_x + 15, y_pos + 20))
        
        # 🆕 Instrucciones en la parte inferior
        instructions = font_desc.render("ENTER/ESPACIO: Seleccionar | ESC: Cancelar | FLECHAS: Navegar", 
                                      True, (150, 150, 150))
        self.screen.blit(instructions, (menu_x + 10, menu_y + menu_height - 25))
    
    def handle_input(self, key):
        """Maneja la entrada del teclado para el menú - MEJORADO"""
        if not self.visible:
            return None
            
        if key == pygame.K_ESCAPE:
            self.hide()
            return "cancel"
        
        # Selección numérica
        elif pygame.K_1 <= key <= pygame.K_9:
            index = key - pygame.K_1
            if index < len(self.abilities):
                return self.select_ability(index)
        
        # Navegación con flechas
        elif key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.abilities)
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.abilities)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.select_ability(self.selected_index)
            
        return None
    
    def select_ability(self, index):
        """Selecciona una habilidad y cierra el menú"""
        self.selected_index = index
        selected_ability = self.abilities[index]
        self.hide()
        return selected_ability
    
    def show(self):
        """Muestra el menú"""
        self.visible = True
        self.selected_index = 0
        print("📋 Menú de habilidades abierto")
    
    def hide(self):
        """Oculta el menú"""
        self.visible = False
        print("❌ Menú de habilidades cerrado")