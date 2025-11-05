import pygame
from game.systems.grid_system import GridSystem
from game.systems.turn_system import TurnSystem
from game.systems.ability_system import AbilitySystem
from game.systems.effect_system import EffectSystem, EffectType
from game.systems.passive_system import PassiveSystem
from game.ui.ability_menu import AbilityMenu
from game.characters.character_factory import CharacterFactory
from game.entities.enemy import Enemy

class BattleScene:
    def __init__(self, screen, player_party_ids=None, enemy_configs=None):
        self.screen = screen
        self.grid = GridSystem()
        self.turn_system = TurnSystem()
        self.ability_system = AbilitySystem(self.grid)
        self.effect_system = EffectSystem()
        self.passive_system = PassiveSystem()
        self.entities = []
        self.selected_entity = None
        self.ability_menu = None
        
        # 🎯 OPTIMIZADO: Sistema de estados unificado
        self.current_state = "idle"  # idle, movement, ability_selection
        self.movement_path = []
        self.movement_range = 0
        self.confirmed_dash_targets = []
        
        player_party_ids = player_party_ids or ["ricchard", "red_thunder", "zoe"]
        enemy_configs = enemy_configs or [
            {"position": (7, 3), "name": "Orco"}, {"position": (7, 5), "name": "Goblin"}
        ]
        
        self.setup_scalable_scenario(player_party_ids, enemy_configs)
        self.turn_system.start_player_turn()
    
    def setup_scalable_scenario(self, player_party_ids, enemy_configs):
        start_positions = [(2, 2), (2, 4), (2, 6)]
        player_party = CharacterFactory.create_party(
            player_party_ids[:3], start_positions[:len(player_party_ids)]
        )
        
        for character in player_party:
            if hasattr(character, 'register_passives'):
                character.register_passives(self.passive_system)
        
        enemies = [Enemy(config["position"], "enemy", config.get("name", "Enemigo")) 
                  for config in enemy_configs]
        
        self.entities = player_party + enemies
        print(f"✅ Equipo: {[p.name for p in player_party]}")
        print(f"✅ Enemigos: {[e.name for e in enemies]}")
        print("🎯 M: Modo movimiento | H: Habilidades | ESPACIO: Terminar turno")
    
    # ===== SISTEMA DE ESTADOS OPTIMIZADO =====
    
    def set_state(self, new_state, **kwargs):
        """Cambia el estado actual de forma controlada"""
        old_state = self.current_state
        
        # Limpiar estado anterior
        if old_state == "movement":
            self.movement_path = []
            self.confirmed_dash_targets = []
        elif old_state == "ability_selection":
            self.ability_system.clear_selection()
        
        # Configurar nuevo estado
        self.current_state = new_state
        
        if new_state == "movement":
            self.movement_range = getattr(self.selected_entity, 'movement_range', 3)
            self.movement_path = [self.selected_entity.position]
            print(f"🎯 Modo movimiento: {self.selected_entity.name} (Rango: {self.movement_range})")
        
        print(f"🔄 Estado: {old_state} → {new_state}")
    
    def enter_movement_mode(self):
        """🎯 OPTIMIZADO: Con validación de estado"""
        if not self.selected_entity or self.selected_entity.has_moved:
            return print("❌ No se puede mover: ya se movió este turno")
        
        if self.current_state == "ability_selection":
            return print("❌ Termina la selección de habilidad primero")
        
        self.set_state("movement")
        print("CLIC en enemigo: Marcar embestida | CLIC en vacío: Mover | ENTER: Confirmar")
    
    def cancel_current_mode(self):
        """🎯 OPTIMIZADO: Un solo método para cancelar cualquier modo"""
        if self.current_state == "movement":
            self.set_state("idle")
            print("❌ Movimiento cancelado")
        elif self.current_state == "ability_selection":
            self.ability_system.cancel_selection()
            self.set_state("idle")
        elif self.ability_menu:
            self.ability_menu = None
            print("❌ Menú cancelado")
        else:
            self.clear_selections()
    
    # ===== SISTEMA DE MOVIMIENTO OPTIMIZADO =====
    
    def calculate_path_to_target(self, start, target):
        """Calcula ruta en línea recta optimizada"""
        path = [start]
        current = start
        
        while current != target and len(path) <= self.movement_range:
            dx, dy = 0, 0
            if current[0] < target[0]: dx = 1
            elif current[0] > target[0]: dx = -1
            elif current[1] < target[1]: dy = 1  
            elif current[1] > target[1]: dy = -1
            else: break
            
            next_pos = (current[0] + dx, current[1] + dy)
            
            # Verificar obstáculos (solo aliados, enemigos permiten embestida)
            if any(e.position == next_pos and e.team == self.selected_entity.team 
                   and e != self.selected_entity for e in self.entities):
                break
            
            path.append(next_pos)
            current = next_pos
        
        return path
    
    def handle_movement_click(self, grid_pos):
        """Maneja clics durante modo movimiento"""
        clicked_entity = next((e for e in self.entities if e.position == grid_pos), None)
        
        if clicked_entity and clicked_entity.team == "enemy":
            return self.mark_enemy_for_dash(clicked_entity)
        
        # Movimiento a casilla vacía
        return self.add_position_to_path(grid_pos)
    
    def mark_enemy_for_dash(self, enemy):
        """Marca enemigo para embestida"""
        if enemy in self.confirmed_dash_targets:
            return print(f"❌ {enemy.name} ya marcado")
        
        self.confirmed_dash_targets.append(enemy)
        print(f"🎯 {enemy.name} marcado para embestida")
        return True
    
    def add_position_to_path(self, grid_pos):
        """Añade posición a la ruta con detección de retroceso"""
        # Retroceder si la posición ya está en la ruta
        if grid_pos in self.movement_path:
            idx = self.movement_path.index(grid_pos)
            if idx < len(self.movement_path) - 1:
                self.movement_path = self.movement_path[:idx + 1]
                print(f"↩️ Retrocediendo a {grid_pos}")
                return True
            return False
        
        # Calcular nueva ruta
        start_pos = self.movement_path[-1]
        new_path = self.calculate_path_to_target(start_pos, grid_pos)
        
        # Verificar límite de movimiento
        remaining_moves = self.movement_range - (len(self.movement_path) - 1)
        if len(new_path) - 1 > remaining_moves:
            return print("❌ Movimiento insuficiente")
        
        # Actualizar ruta
        self.movement_path = self.movement_path[:-1] + new_path
        print(f"📍 Moviendo a {grid_pos} ({remaining_moves - (len(new_path) - 1)} restantes)")
        return True
    
    def execute_movement(self):
        """Ejecuta el movimiento completo"""
        if len(self.movement_path) < 2:
            return print("❌ Ruta no válida")
        
        # Aplicar embestidas
        dash_hits = []
        for pos in self.movement_path[1:]:
            for enemy in self.confirmed_dash_targets:
                if enemy.position == pos and enemy not in dash_hits:
                    damage = int(self.selected_entity.stats['attack'] * 0.1)
                    enemy.stats['current_hp'] -= damage
                    dash_hits.append(enemy)
                    print(f"💥 Embistió a {enemy.name} por {damage} daño!")
        
        # Mover personaje
        self.selected_entity.position = self.movement_path[-1]
        self.selected_entity.has_moved = True
        self.set_state("idle")
        
        print(f"✅ Movimiento completado. Embestidas: {len(dash_hits)}")
        return True
    
    # ===== MANEJO DE EVENTOS OPTIMIZADO =====
    
    def handle_event(self, event):
        if self.ability_menu and self.ability_menu.visible:
            return self.handle_ability_menu_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
    
    def handle_ability_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            result = self.ability_menu.handle_input(event.key)
            if result == "cancel":
                self.ability_menu = None
                print("❌ Menú cancelado")
            elif result:
                self.on_ability_selected(result)
    
    def handle_keydown(self, event):
        # 🎯 OPTIMIZADO: Mapeo más claro de teclas
        key_actions = {
            pygame.K_SPACE: self.end_turn,
            pygame.K_ESCAPE: self.cancel_current_mode,
            pygame.K_h: lambda: self.open_ability_menu() if self.selected_entity else None,
            pygame.K_m: lambda: self.enter_movement_mode() if self.selected_entity else None,
            pygame.K_RETURN: lambda: self.execute_movement() if self.current_state == "movement" else None
        }
        
        handler = key_actions.get(event.key)
        if handler:
            handler()
    
    def handle_click(self, pos):
        grid_pos = self.grid.get_grid_position(pos)
        if not self.grid.is_valid_position(grid_pos):
            return
        
        # 🎯 OPTIMIZADO: Delegar según estado actual
        if self.current_state == "movement":
            self.handle_movement_click(grid_pos)
        elif self.current_state == "ability_selection":
            success = self.ability_system.handle_click(grid_pos, self.entities)
            if success:
                self.set_state("idle")  # Vuelve a idle si la habilidad se ejecutó
        else:  # Estado idle
            self.handle_idle_click(grid_pos)
    
    def handle_idle_click(self, grid_pos):
        """Maneja clics en estado idle (selección y ataque básico)"""
        # Selección de aliado
        for entity in self.entities:
            if entity.position == grid_pos and self.turn_system.can_select(entity):
                self.selected_entity = entity
                self.set_state("idle")
                print(f"✅ {entity.name} seleccionado")
                return
        
        if not self.selected_entity:
            return
        
        # Ataque básico
        enemy = next((e for e in self.entities if e.position == grid_pos and e.team == "enemy"), None)
        if enemy and not self.selected_entity.has_acted:
            self.selected_entity.basic_attack(enemy)
    
    # ===== SISTEMA DE HABILIDADES OPTIMIZADO =====
    
    def open_ability_menu(self):
        if not self.selected_entity or self.selected_entity.has_acted:
            return print("❌ No se puede usar habilidades")
        
        if self.current_state == "movement":
            return print("❌ Termina el movimiento primero")
        
        screen_pos = self.grid.get_screen_position(self.selected_entity.position)
        self.ability_menu = AbilityMenu(self.screen, self.selected_entity, screen_pos)
        self.ability_menu.show()
    
    def on_ability_selected(self, ability_data):
        print(f"🎯 {self.selected_entity.name} prepara {ability_data['name']}")
        
        # Activar el modo de selección según el tipo de habilidad
        if self.ability_system.select_ability(ability_data, self.selected_entity, self.entities):
            self.set_state("ability_selection")
        
        self.ability_menu = None
    
    def clear_selections(self):
        self.selected_entity = None
        self.ability_system.clear_selection()
        self.ability_menu = None
        self.set_state("idle")
    
    def update(self):
        if self.current_state == "movement":
            self.update_movement_preview(pygame.mouse.get_pos())
    
    def update_movement_preview(self, cursor_pos):
        """Actualiza la previsualización de movimiento"""
        grid_pos = self.grid.get_grid_position(cursor_pos)
        if not self.grid.is_valid_position(grid_pos):
            return
        
        start_pos = self.movement_path[-1]
        preview_path = self.calculate_path_to_target(start_pos, grid_pos)
        
        # Limitar por movimiento restante
        remaining = self.movement_range - (len(self.movement_path) - 1)
        if len(preview_path) - 1 > remaining:
            preview_path = preview_path[:remaining + 1]
        
        self.movement_path = self.movement_path[:-1] + preview_path
    
    def draw(self):
        self.screen.fill((30, 30, 60))
        self.grid.draw(self.screen)
        
        # Dibujar según estado actual
        if self.current_state == "movement" and len(self.movement_path) > 1:
            self.draw_movement_preview()
        
        if self.current_state == "ability_selection":
            self.ability_system.draw_target_indicators(self.screen)
        
        # Dibujar entidades
        for entity in self.entities:
            entity.draw(self.screen, self.grid)
        
        if self.ability_menu:
            self.ability_menu.draw()
        
        self.draw_ui()
    
    def draw_movement_preview(self):
        """Dibuja la ruta de movimiento"""
        # Línea de trayectoria
        for i in range(len(self.movement_path) - 1):
            start = self.grid.get_screen_position(self.movement_path[i])
            end = self.grid.get_screen_position(self.movement_path[i + 1])
            start_center = (start[0] + self.grid.cell_size // 2, start[1] + self.grid.cell_size // 2)
            end_center = (end[0] + self.grid.cell_size // 2, end[1] + self.grid.cell_size // 2)
            pygame.draw.line(self.screen, (100, 255, 100), start_center, end_center, 4)
        
        # Casillas de la ruta
        for pos in self.movement_path[1:]:
            screen_pos = self.grid.get_screen_position(pos)
            rect = pygame.Rect(screen_pos[0], screen_pos[1], self.grid.cell_size, self.grid.cell_size)
            highlight = pygame.Surface((self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA)
            highlight.fill((100, 255, 100, 80))
            self.screen.blit(highlight, rect)
            pygame.draw.rect(self.screen, (50, 255, 50), rect, 3)
        
        # Enemigos marcados
        for enemy in self.confirmed_dash_targets:
            screen_pos = self.grid.get_screen_position(enemy.position)
            center = (screen_pos[0] + self.grid.cell_size // 2, screen_pos[1] + self.grid.cell_size // 2)
            pygame.draw.circle(self.screen, (255, 50, 50), center, 25, 4)
            
            damage = int(self.selected_entity.stats['attack'] * 0.1)
            font = pygame.font.SysFont(None, 20)
            self.screen.blit(font.render(f"-{damage}", True, (255, 100, 100)), 
                           (center[0] - 10, center[1] - 35))
            self.screen.blit(font.render("EMBESTIDA", True, (255, 100, 100)), 
                           (center[0] - 30, center[1] + 20))
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario optimizada"""
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        # Información del turno
        turn_text = f"Turno: {self.turn_system.current_turn} ({self.turn_system.turn_count})"
        self.screen.blit(font.render(turn_text, True, (255, 255, 255)), (20, 20))
        
        # Información del personaje seleccionado
        if self.selected_entity:
            # 🎯 INFORMACIÓN DE ENERGÍA MEJORADA
            current_energy = self.selected_entity.get_energy_absolute()
            max_energy = self.selected_entity.energy_stats['max_energy']
            energy_percentage = self.selected_entity.get_energy_percentage()
            
            info_lines = [
                f"Seleccionado: {self.selected_entity.name}",
                f"Movimiento: {'✅' if not self.selected_entity.has_moved else '❌'}",
                f"Acción: {'✅' if not self.selected_entity.has_acted else '❌'}",
                f"PH: {self.selected_entity.stats['current_ph']}/{self.selected_entity.stats['max_ph']}",
                f"HP: {self.selected_entity.stats['current_hp']}/{self.selected_entity.stats['max_hp']}",
                f"Energía: {current_energy}/{max_energy}",
                f"Rango Mov: {getattr(self.selected_entity, 'movement_range', 3)}",
                f"Estado: {self.current_state.upper()}"
            ]
            
            # 🎯 BARRA DE ENERGÍA VISUAL
            energy_width = 200
            energy_fill = int(energy_width * (energy_percentage / 100))
            
            # Fondo barra
            pygame.draw.rect(self.screen, (50, 50, 50), (20, 210, energy_width, 20))
            # Barra de energía
            energy_color = (100, 200, 255)
            if energy_percentage >= 100:
                energy_color = (255, 215, 0)  # Dorado cuando está lista
            pygame.draw.rect(self.screen, energy_color, (20, 210, energy_fill, 20))
            # Borde
            pygame.draw.rect(self.screen, (200, 200, 200), (20, 210, energy_width, 20), 2)
            
            # Texto energía
            energy_text = f"ENERGÍA: {current_energy}/{max_energy}"
            if energy_percentage >= 100:
                energy_text += " - ULTIMATE LISTA! 💥"
            self.screen.blit(small_font.render(energy_text, True, (255, 255, 255)), (25, 212))
            
            # 🎯 MOSTRAR COSTOS DE ULTIMATE DISPONIBLES
            ultimate_cost = None
            ultimate_name = None
            for ability_key, ability_config in self.selected_entity.abilities_config.items():
                if ability_config.get('is_ultimate', False):
                    ultimate_cost = ability_config.get('energy_cost', 100)
                    ultimate_name = ability_config.get('name', 'Ultimate')
                    break
            
            if ultimate_cost:
                cost_text = f"Ultimate: {ultimate_name} - Costo: {ultimate_cost}"
                cost_color = (100, 255, 100) if current_energy >= ultimate_cost else (255, 100, 100)
                self.screen.blit(small_font.render(cost_text, True, cost_color), (25, 235))
            
            for i, text in enumerate(info_lines):
                self.screen.blit(small_font.render(text, True, (255, 255, 255)), (20, 60 + i * 25))
        
        # Instrucciones según estado
        instructions = self.get_instructions()
        for i, instruction in enumerate(instructions):
            self.screen.blit(small_font.render(instruction, True, (150, 200, 255)), 
                        (20, 500 + i * 30))
    
    def get_instructions(self):
        if self.current_state == "movement":
            base = [
                "MODO MOVIMIENTO ACTIVO",
                "CLIC en enemigo: Marcar embestida", 
                "CLIC en vacío: Mover/Retroceder",
                "ENTER: Confirmar movimiento",
                "ESC: Cancelar movimiento"
            ]
            if self.confirmed_dash_targets:
                base.append(f"🎯 Enemigos marcados: {len(self.confirmed_dash_targets)}")
            return base
        elif self.current_state == "ability_selection":
            return ["CLIC: Seleccionar objetivo", "ESC: Cancelar habilidad"]
        elif self.selected_entity:
            return ["M: Modo movimiento", "H: Habilidades", "CLIC en enemigo: Atacar"]
        return ["ESPACIO: Terminar turno"]
    
    def end_turn(self):
        print("🔄 Terminando turno...")
        self.effect_system.update_effects(self.entities)
        self.set_state("idle")
        
        for entity in self.entities:
            if entity.team == self.turn_system.current_turn:
                entity.reset_turn()
        
        self.clear_selections()
        self.turn_system.end_turn()
        
        if self.turn_system.current_turn == "enemy":
            self.do_enemy_turn()
    
    def do_enemy_turn(self):
        print("🤖 Turno del enemigo...")
        for entity in self.entities:
            if entity.team == "enemy" and not entity.has_acted:
                entity.has_acted = True
        
        pygame.time.set_timer(pygame.USEREVENT, 1000)