import pygame
from game.core.event_system import event_system, EventTypes

class SelectionMode:
    """Clase base para todos los modos de selección"""
    
    def __init__(self, mode_type, ability_system):
        self.mode_type = mode_type
        self.ability_system = ability_system
        self.is_active = False
        self.targets = []
    
    def activate(self, ability_data, caster, entities):
        self.is_active = True
        self.ability_data = ability_data
        self.caster = caster
        self.targets = []
        return True
    
    def deactivate(self):
        self.is_active = False
        self.targets = []
    
    def handle_click(self, grid_pos, entities):
        raise NotImplementedError
    
    def draw_indicators(self, screen):
        raise NotImplementedError
    
    def cancel_selection(self):
        self.deactivate()
        return True

class NoTargetSelectionMode(SelectionMode):
    """Modo sin objetivo - se ejecuta inmediatamente"""
    
    def __init__(self, ability_system):
        super().__init__('none', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        # 🎯 EJECUCIÓN INMEDIATA - sin necesidad de clic
        context = self.ability_system.create_context()
        success = self.ability_system.execute_ability_directly(context)
        self.deactivate()
        return success
    
    def handle_click(self, grid_pos, entities):
        return False  # No maneja clics
    
    def draw_indicators(self, screen):
        pass  # No dibuja nada

class SelfSelectionMode(SelectionMode):
    """Modo de auto-aplicación (solo necesita el caster)"""
    
    def __init__(self, ability_system):
        super().__init__('self', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        # 🎯 EJECUCIÓN INMEDIATA en el caster
        context = self.ability_system.create_context(target_entity=caster)
        success = self.ability_system.execute_ability_directly(context)
        self.deactivate()
        return success
    
    def handle_click(self, grid_pos, entities):
        return False
    
    def draw_indicators(self, screen):
        pass

class AllySelectionMode(SelectionMode):
    """Modo para seleccionar aliados (como Grito de Tempestad)"""
    
    def __init__(self, ability_system):
        super().__init__('ally', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        range_distance = ability_data.get('range', 1)
        self.targets = [
            entity for entity in entities
            if (entity.team == caster.team and 
                entity != caster and  # No seleccionarse a sí mismo
                self.calculate_distance(caster.position, entity.position) <= range_distance)
        ]
        
        print(f"🛡️ Modo ALIADO: {len(self.targets)} aliados encontrados")
        return len(self.targets) > 0
    
    def handle_click(self, grid_pos, entities):
        for entity in entities:
            if entity.position == grid_pos and entity in self.targets:
                context = self.ability_system.create_context(target_entity=entity)
                return self.ability_system.execute_ability_directly(context)
        
        print("❌ No hay un aliado válido en esta posición")
        return False
    
    def draw_indicators(self, screen):
        for target in self.targets:
            screen_pos = self.ability_system.grid_system.get_screen_position(target.position)
            center_x = screen_pos[0] + self.ability_system.grid_system.cell_size // 2
            center_y = screen_pos[1] + self.ability_system.grid_system.cell_size // 2
            
            radius = self.ability_system.grid_system.cell_size // 2 + 8
            pygame.draw.circle(screen, (100, 200, 255), (center_x, center_y), radius, 4)
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class EnemySelectionMode(SelectionMode):
    """Modo para seleccionar enemigos (como AMP básico)"""
    
    def __init__(self, ability_system):
        super().__init__('enemy', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        range_distance = ability_data.get('range', 1)
        self.targets = [
            entity for entity in entities
            if (entity.team != caster.team and 
                self.calculate_distance(caster.position, entity.position) <= range_distance)
        ]
        
        print(f"🎯 Modo ENEMIGO: {len(self.targets)} objetivos encontrados")
        return len(self.targets) > 0
    
    def handle_click(self, grid_pos, entities):
        for entity in entities:
            if entity.position == grid_pos and entity in self.targets:
                context = self.ability_system.create_context(target_entity=entity)
                return self.ability_system.execute_ability_directly(context)
        
        print("❌ No hay un objetivo válido en esta posición")
        return False
    
    def draw_indicators(self, screen):
        for target in self.targets:
            screen_pos = self.ability_system.grid_system.get_screen_position(target.position)
            center_x = screen_pos[0] + self.ability_system.grid_system.cell_size // 2
            center_y = screen_pos[1] + self.ability_system.grid_system.cell_size // 2
            
            radius = self.ability_system.grid_system.cell_size // 2 + 8
            pygame.draw.circle(screen, (255, 50, 50), (center_x, center_y), radius, 4)
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class PositionSelectionMode(SelectionMode):
    """Modo para seleccionar posición (como Destello Vácuo)"""
    
    def __init__(self, ability_system):
        super().__init__('position', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        range_distance = ability_data.get('range', 1)
        caster_x, caster_y = caster.position
        self.targets = []
        
        for x in range(caster_x - range_distance, caster_x + range_distance + 1):
            for y in range(caster_y - range_distance, caster_y + range_distance + 1):
                distance = abs(x - caster_x) + abs(y - caster_y)
                if (distance <= range_distance and 
                    self.ability_system.grid_system.is_valid_position((x, y)) and
                    (x, y) != caster.position):
                    self.targets.append((x, y))
        
        print(f"📍 Modo POSICIÓN: {len(self.targets)} posiciones válidas")
        return len(self.targets) > 0
    
    def handle_click(self, grid_pos, entities):
        if grid_pos in self.targets:
            context = self.ability_system.create_context(target_position=grid_pos)
            return self.ability_system.execute_ability_directly(context)
        
        print("❌ Posición fuera de rango")
        return False
    
    def draw_indicators(self, screen):
        for pos in self.targets:
            screen_pos = self.ability_system.grid_system.get_screen_position(pos)
            rect = pygame.Rect(
                screen_pos[0], screen_pos[1],
                self.ability_system.grid_system.cell_size,
                self.ability_system.grid_system.cell_size
            )
            
            highlight_surface = pygame.Surface((self.ability_system.grid_system.cell_size, 
                                              self.ability_system.grid_system.cell_size), 
                                              pygame.SRCALPHA)
            highlight_surface.fill((100, 255, 100, 80))
            screen.blit(highlight_surface, rect)
            pygame.draw.rect(screen, (50, 255, 50), rect, 3)

class ChainSelectionMode(SelectionMode):
    """Modo para selección en cadena (como Corte Fugaz) - CORREGIDO"""
    
    def __init__(self, ability_system):
        super().__init__('chain', ability_system)
        self.selected_targets = []
        self.available_targets = []
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        self.max_targets = ability_data.get('max_targets', 3)
        self.min_targets = ability_data.get('min_targets', 1)
        self.selected_targets = []
        self.available_targets = self.calculate_initial_targets(entities)
        
        print(f"⛓️ Modo CADENA: Selecciona de {self.min_targets} a {self.max_targets} objetivos")
        print(f"   Objetivos iniciales: {len(self.available_targets)}")
        print("   CLIC en enemigo: Añadir objetivo")
        print("   CLIC en vacío: Confirmar con objetivos actuales")
        print("   ESC: Cancelar habilidad")
        return len(self.available_targets) >= self.min_targets
    
    def calculate_initial_targets(self, entities):
        # 🎯 CORRECCIÓN: Usar el rango configurado en la habilidad
        range_distance = self.ability_data.get('range', 1)
        
        initial_targets = [
            entity for entity in entities
            if (entity.team != self.caster.team and 
                self.calculate_distance(self.caster.position, entity.position) <= range_distance)
        ]
        
        print(f"🎯 Objetivos iniciales encontrados: {len(initial_targets)}")
        return initial_targets
    
    def calculate_next_targets(self, last_target, entities):
        # 🎯 CORRECCIÓN: Usar el rango configurado en la habilidad
        range_distance = self.ability_data.get('range', 1)
        
        return [
            entity for entity in entities
            if (entity.team != self.caster.team and 
                entity not in self.selected_targets and
                self.calculate_distance(last_target.position, entity.position) <= range_distance)
        ]
    
    def handle_click(self, grid_pos, entities):
        clicked_entity = None
        for entity in entities:
            if entity.position == grid_pos:
                clicked_entity = entity
                break
        
        # CONFIRMAR CON CLIC EN VACÍO SI TENEMOS AL MENOS EL MÍNIMO
        if not clicked_entity:
            if len(self.selected_targets) >= self.min_targets:
                return self.execute_chain_attack()
            else:
                print(f"❌ Necesitas al menos {self.min_targets} objetivo(s)")
                return False
        
        if clicked_entity and clicked_entity in self.available_targets:
            self.selected_targets.append(clicked_entity)
            print(f"⛓️ Objetivo {len(self.selected_targets)} seleccionado: {clicked_entity.name}")
            
            # EJECUTAR INMEDIATAMENTE SI ALCANZAMOS EL MÁXIMO
            if len(self.selected_targets) >= self.max_targets:
                return self.execute_chain_attack()
            else:
                self.available_targets = self.calculate_next_targets(clicked_entity, entities)
                print(f"   Próximos objetivos disponibles: {len(self.available_targets)}")
                
                # SI NO HAY MÁS OBJETIVOS PERO TENEMOS EL MÍNIMO, PERMITIR CONFIRMAR
                if not self.available_targets and len(self.selected_targets) >= self.min_targets:
                    print("   ⚠️  No hay más objetivos en cadena. Clíc en vacío para confirmar.")
                
                return False
        
        print("❌ Objetivo no válido para la cadena")
        return False
    
    def execute_chain_attack(self):
        """EJECUTAR ATAQUE EN CADENA CON LOS OBJETIVOS SELECCIONADOS"""
        print(f"🎯 Ejecutando cadena con {len(self.selected_targets)} objetivos")
        context = self.ability_system.create_context()
        context.entities = self.selected_targets
        success = self.ability_system.execute_ability_directly(context)
        self.deactivate()
        return success
    
    def draw_indicators(self, screen):
        for target in self.available_targets:
            screen_pos = self.ability_system.grid_system.get_screen_position(target.position)
            center_x = screen_pos[0] + self.ability_system.grid_system.cell_size // 2
            center_y = screen_pos[1] + self.ability_system.grid_system.cell_size // 2
            
            radius = self.ability_system.grid_system.cell_size // 2 + 8
            pygame.draw.circle(screen, (50, 150, 255), (center_x, center_y), radius, 4)
        
        for i, target in enumerate(self.selected_targets):
            screen_pos = self.ability_system.grid_system.get_screen_position(target.position)
            center_x = screen_pos[0] + self.ability_system.grid_system.cell_size // 2
            center_y = screen_pos[1] + self.ability_system.grid_system.cell_size // 2
            
            radius = self.ability_system.grid_system.cell_size // 2 + 6
            pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), radius, 4)
            
            font = pygame.font.SysFont(None, 24)
            order_text = font.render(str(i+1), True, (255, 215, 0))
            screen.blit(order_text, (center_x - order_text.get_width() // 2, center_y - 10))
    
    def cancel_selection(self):
        print("❌ Selección en cadena cancelada")
        self.deactivate()
        return True
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
class GlobalAllySelectionMode(SelectionMode):
    """Modo para seleccionar cualquier aliado en el mapa"""
    
    def __init__(self, ability_system):
        super().__init__('global_ally', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        self.targets = [
            entity for entity in entities
            if entity.team == caster.team and entity != caster
        ]
        
        print(f"🌍 Modo ALIADO GLOBAL: {len(self.targets)} aliados disponibles")
        return len(self.targets) > 0
    
    def handle_click(self, grid_pos, entities):
        for entity in entities:
            if entity.position == grid_pos and entity in self.targets:
                context = self.ability_system.create_context(target_entity=entity)
                return self.ability_system.execute_ability_directly(context)
        
        print("❌ No hay un aliado válido en esta posición")
        return False
    
    def draw_indicators(self, screen):
        for target in self.targets:
            screen_pos = self.ability_system.grid_system.get_screen_position(target.position)
            center_x = screen_pos[0] + self.ability_system.grid_system.cell_size // 2
            center_y = screen_pos[1] + self.ability_system.grid_system.cell_size // 2
            
            radius = self.ability_system.grid_system.cell_size // 2 + 8
            pygame.draw.circle(screen, (100, 200, 255), (center_x, center_y), radius, 4)

class GlobalSelfSelectionMode(SelectionMode):
    """Modo que se auto-ejecuta globalmente"""
    
    def __init__(self, ability_system):
        super().__init__('global_self', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        # Ejecutar inmediatamente
        context = self.ability_system.create_context(target_entity=caster)
        success = self.ability_system.execute_ability_directly(context)
        self.deactivate()
        return success
    
    def handle_click(self, grid_pos, entities):
        return False
    
    def draw_indicators(self, screen):
        pass

class SelectionSystem:
    def __init__(self, ability_system):
        self.ability_system = ability_system
        self.active_mode = None
        
        self.modes = {
            'none': NoTargetSelectionMode(ability_system),
            'self': SelfSelectionMode(ability_system),
            'ally': AllySelectionMode(ability_system),
            'enemy': EnemySelectionMode(ability_system),
            'position': PositionSelectionMode(ability_system),
            'chain': ChainSelectionMode(ability_system),
            'global_ally': GlobalAllySelectionMode(ability_system),
            'global_self': GlobalSelfSelectionMode(ability_system),
            'line': LineSelectionMode(ability_system),      
            'aoe': AoeSelectionMode(ability_system)         
        }
    
    def activate_mode(self, mode_name, ability_data, caster, entities):
        if self.active_mode:
            self.active_mode.deactivate()
        
        if mode_name in self.modes:
            self.active_mode = self.modes[mode_name]
            success = self.active_mode.activate(ability_data, caster, entities)
            if not success:
                print(f"❌ No se pudo activar el modo {mode_name} - no hay objetivos válidos")
            return success
        
        print(f"❌ Modo de selección desconocido: {mode_name}")
        print(f"   Modos disponibles: {list(self.modes.keys())}")
        return False
    
    def handle_click(self, grid_pos, entities):
        if self.active_mode and self.active_mode.is_active:
            return self.active_mode.handle_click(grid_pos, entities)
        return False
    
    def draw_indicators(self, screen):
        if self.active_mode and self.active_mode.is_active:
            self.active_mode.draw_indicators(screen)
    
    def cancel_selection(self):
        if self.active_mode:
            return self.active_mode.cancel_selection()
        return False
    
    def is_active(self):
        return self.active_mode and self.active_mode.is_active
    
    def get_current_mode_type(self):
        if self.active_mode:
            return self.active_mode.mode_type
        return None

class LineSelectionMode(SelectionMode):
    """Modo para habilidades en línea (como Carrera Relámpago) - CORREGIDO"""
    
    def __init__(self, ability_system):
        super().__init__('line', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        print(f"➖ Modo LÍNEA: Selecciona dirección para {ability_data['name']}")
        return True
    
    def handle_click(self, grid_pos, entities):
        # Para modo línea, el clic define la dirección
        caster_pos = self.caster.position
        
        # Dirección aproximada
        dx = grid_pos[0] - caster_pos[0]
        dy = grid_pos[1] - caster_pos[1]
        
        # Normalizar dirección (línea recta)
        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)
        
        # 🎯 CORRECCIÓN: Encontrar TODAS las entidades en la línea, no solo enemigos
        line_targets = []
        current_pos = caster_pos
        range_distance = self.ability_data.get('range', 10)
        
        for i in range(range_distance):
            current_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            
            # Verificar si la posición es válida
            if not self.ability_system.grid_system.is_valid_position(current_pos):
                break
            
            # 🎯 BUSCAR TODAS LAS ENTIDADES, NO SOLO ENEMIGOS
            for entity in entities:
                if entity.position == current_pos:
                    line_targets.append(entity)
        
        # 🎯 CORRECCIÓN: Ejecutar la habilidad aunque no haya objetivos
        # Las habilidades de movilidad deben funcionar igual
        context = self.ability_system.create_context()
        context.entities = line_targets  # Puede estar vacío
        
        # 🎯 AÑADIR LA DIRECCIÓN AL CONTEXTO PARA EFECTOS DE MOVIMIENTO
        context.extra_data = {
            'direction': direction,
            'line_length': min(range_distance, self._calculate_line_length(caster_pos, direction, range_distance))
        }
        
        success = self.ability_system.execute_ability_directly(context)
        
        if not success:
            print("⚠️  Habilidad ejecutada sin objetivos - movimiento puro")
        
        return success
    
    def _calculate_line_length(self, start_pos, direction, max_range):
        """Calcula cuánto puede avanzar en la dirección sin obstáculos"""
        from game.systems.grid_system import GridSystem
        grid_system = GridSystem()
        
        current_pos = start_pos
        length = 0
        
        for i in range(max_range):
            next_pos = (current_pos[0] + direction[0], current_pos[1] + direction[1])
            
            if not grid_system.is_valid_position(next_pos):
                break
            
            # Verificar si hay obstáculos (solo aliados bloquean)
            # Los enemigos no deberían bloquear habilidades de movimiento
            # Esta lógica puede ajustarse por habilidad
            
            current_pos = next_pos
            length += 1
        
        return length
    
    def draw_indicators(self, screen):
        # Dibujar líneas en las 4 direcciones principales
        caster_pos = self.caster.position
        screen_pos = self.ability_system.grid_system.get_screen_position(caster_pos)
        cell_size = self.ability_system.grid_system.cell_size
        
        center_x = screen_pos[0] + cell_size // 2
        center_y = screen_pos[1] + cell_size // 2
        
        # Líneas en 4 direcciones
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        colors = [(100, 255, 100), (100, 255, 100), (100, 255, 100), (100, 255, 100)]  # Verde para movimiento
        
        range_distance = self.ability_data.get('range', 10)
        
        for i, (dx, dy) in enumerate(directions):
            end_x = center_x + dx * cell_size * range_distance
            end_y = center_y + dy * cell_size * range_distance
            pygame.draw.line(screen, colors[i], (center_x, center_y), (end_x, end_y), 3)
            
            # Dibujar círculo al final de la línea
            pygame.draw.circle(screen, colors[i], (int(end_x), int(end_y)), 8, 2)

class AoeSelectionMode(SelectionMode):
    """Modo para AOE alrededor del caster (como Red Thunderblast)"""
    
    def __init__(self, ability_system):
        super().__init__('aoe', ability_system)
    
    def activate(self, ability_data, caster, entities):
        super().activate(ability_data, caster, entities)
        
        # Ejecutar inmediatamente en área alrededor del caster
        aoe_radius = ability_data.get('aoe_radius', 1)
        targets = [
            entity for entity in entities
            if (entity.team != caster.team and 
                self.calculate_distance(caster.position, entity.position) <= aoe_radius)
        ]
        
        context = self.ability_system.create_context()
        context.entities = targets
        success = self.ability_system.execute_ability_directly(context)
        self.deactivate()
        return success
    
    def handle_click(self, grid_pos, entities):
        return False  # No necesita clic
    
    def draw_indicators(self, screen):
        # Dibujar área AOE alrededor del caster
        caster_pos = self.caster.position
        screen_pos = self.ability_system.grid_system.get_screen_position(caster_pos)
        cell_size = self.ability_system.grid_system.cell_size
        
        aoe_radius = self.ability_data.get('aoe_radius', 1)
        
        for dx in range(-aoe_radius, aoe_radius + 1):
            for dy in range(-aoe_radius, aoe_radius + 1):
                if abs(dx) + abs(dy) <= aoe_radius:
                    pos = (caster_pos[0] + dx, caster_pos[1] + dy)
                    if self.ability_system.grid_system.is_valid_position(pos):
                        target_screen_pos = self.ability_system.grid_system.get_screen_position(pos)
                        rect = pygame.Rect(
                            target_screen_pos[0], target_screen_pos[1],
                            cell_size, cell_size
                        )
                        highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        highlight.fill((255, 100, 100, 80))
                        screen.blit(highlight, rect)
                        pygame.draw.rect(screen, (255, 50, 50), rect, 2)
    
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])