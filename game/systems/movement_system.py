# game/systems/movement_system.py
import pygame
from typing import List, Tuple, Optional
from game.core.event_system import event_system, EventTypes

class MovementSystem:
    """
    Sistema dedicado para manejar movimiento y embestidas.
    Extraído de BattleScene para separar responsabilidades.
    """
    
    def __init__(self, grid_system):
        self.grid = grid_system
        self.reset()
    
    def reset(self):
        """Reinicia completamente el estado del movimiento"""
        self.entity = None
        self.movement_path = []
        self.dash_targets = []
        self.movement_range = 0
        self.is_active = False
    
    def start_movement(self, entity, all_entities: List) -> bool:
        """
        Inicia el modo movimiento para una entidad.
        Retorna True si se pudo iniciar correctamente.
        """
        if not entity:
            print("❌ No hay entidad seleccionada")
            return False
            
        if entity.has_moved:
            print(f"❌ {entity.name} ya se movió este turno")
            return False
        
        self.entity = entity
        self.movement_range = getattr(entity, 'movement_range', 3)
        self.movement_path = [entity.position]
        self.dash_targets = []
        self.is_active = True
        
        print(f"🎯 Modo movimiento: {entity.name} (Rango: {self.movement_range})")
        return True
    
    def handle_click(self, grid_pos: Tuple[int, int], all_entities: List) -> bool:
        """
        Maneja clic durante modo movimiento.
        Retorna True si el clic fue procesado.
        """
        if not self.is_active or not self.entity:
            return False
        
        clicked_entity = next((e for e in all_entities if e.position == grid_pos), None)
        
        if clicked_entity and clicked_entity.team == "enemy":
            return self._mark_dash_target(clicked_entity)
        
        return self._add_to_path(grid_pos, all_entities)
    
    def _mark_dash_target(self, enemy) -> bool:
        """Marca un enemigo para embestida"""
        if enemy in self.dash_targets:
            print(f"❌ {enemy.name} ya está marcado para embestida")
            return False
        
        self.dash_targets.append(enemy)
        print(f"🎯 {enemy.name} marcado para embestida")
        return True
    
    def _add_to_path(self, grid_pos: Tuple[int, int], all_entities: List) -> bool:
        """
        Añade una posición a la ruta de movimiento.
        Maneja tanto movimiento nuevo como retroceso.
        """
        # Detectar retroceso (clic en posición ya visitada)
        if grid_pos in self.movement_path:
            idx = self.movement_path.index(grid_pos)
            if idx < len(self.movement_path) - 1:
                self.movement_path = self.movement_path[:idx + 1]
                print(f"↩️ Retrocediendo a {grid_pos}")
                return True
            return False
        
        # Calcular nueva ruta desde la última posición
        start_pos = self.movement_path[-1]
        new_segment = self._calculate_path_segment(start_pos, grid_pos, all_entities)
        
        if not new_segment or len(new_segment) < 2:
            return False
        
        # Verificar que no exceda el movimiento disponible
        remaining_moves = self.movement_range - (len(self.movement_path) - 1)
        if len(new_segment) - 1 > remaining_moves:
            print("❌ Movimiento excede el rango disponible")
            return False
        
        # Actualizar ruta
        self.movement_path = self.movement_path[:-1] + new_segment
        moves_used = len(new_segment) - 1
        print(f"📍 Ruta actualizada: {moves_used} movimientos usados, {remaining_moves - moves_used} restantes")
        return True
    
    def _calculate_path_segment(self, start: Tuple[int, int], end: Tuple[int, int], 
                              all_entities: List) -> List[Tuple[int, int]]:
        """
        Calcula un segmento de ruta en línea recta entre dos puntos.
        Considera obstáculos (aliados).
        """
        path = [start]
        current = start
        
        while current != end and len(path) <= self.movement_range:
            # Calcular dirección
            dx, dy = 0, 0
            if current[0] < end[0]: dx = 1
            elif current[0] > end[0]: dx = -1
            elif current[1] < end[1]: dy = 1  
            elif current[1] > end[1]: dy = -1
            else: break
            
            next_pos = (current[0] + dx, current[1] + dy)
            
            # Verificar obstáculos (solo aliados bloquean)
            if any(e.position == next_pos and e.team == self.entity.team 
                   and e != self.entity for e in all_entities):
                break
            
            path.append(next_pos)
            current = next_pos
        
        return path
    
    def execute_movement(self) -> bool:
        """
        Ejecuta el movimiento completo, incluyendo embestidas.
        Retorna True si el movimiento fue exitoso.
        """
        if not self.is_active or len(self.movement_path) < 2:
            print("❌ No hay movimiento que ejecutar")
            return False
        
        # Aplicar daño de embestidas
        dash_damage = 0
        dash_hits = []
        
        for pos in self.movement_path[1:]:
            for enemy in self.dash_targets:
                if enemy.position == pos and enemy not in dash_hits:
                    damage = int(self.entity.stats['attack'] * 0.1)
                    enemy.stats['current_hp'] -= damage
                    dash_damage += damage
                    dash_hits.append(enemy)
                    print(f"💥 Embistió a {enemy.name} por {damage} daño!")
        
        # Mover entidad
        final_position = self.movement_path[-1]
        self.entity.position = final_position
        self.entity.has_moved = True
        
        print(f"✅ Movimiento completado a {final_position}. Embestidas: {len(dash_hits)} ({dash_damage} daño total)")
        
        self.reset()
        return True
    
    def update_preview(self, cursor_pos: Tuple[int, int], all_entities: List):
        """Actualiza la previsualización de la ruta"""
        if not self.is_active:
            return
        
        grid_pos = self.grid.get_grid_position(cursor_pos)
        if not self.grid.is_valid_position(grid_pos):
            return
        
        start_pos = self.movement_path[-1]
        preview_segment = self._calculate_path_segment(start_pos, grid_pos, all_entities)
        
        if not preview_segment or len(preview_segment) < 2:
            return
        
        # Limitar por movimiento restante
        remaining = self.movement_range - (len(self.movement_path) - 1)
        if len(preview_segment) - 1 > remaining:
            preview_segment = preview_segment[:remaining + 1]
        
        self.movement_path = self.movement_path[:-1] + preview_segment
    
    def draw(self, screen):
        """Dibuja la ruta de movimiento y embestidas"""
        if not self.is_active or len(self.movement_path) < 2:
            return
        
        # Línea de trayectoria
        for i in range(len(self.movement_path) - 1):
            start = self.grid.get_screen_position(self.movement_path[i])
            end = self.grid.get_screen_position(self.movement_path[i + 1])
            start_center = (start[0] + self.grid.cell_size // 2, start[1] + self.grid.cell_size // 2)
            end_center = (end[0] + self.grid.cell_size // 2, end[1] + self.grid.cell_size // 2)
            pygame.draw.line(screen, (100, 255, 100), start_center, end_center, 4)
        
        # Casillas de la ruta
        for pos in self.movement_path[1:]:
            screen_pos = self.grid.get_screen_position(pos)
            rect = pygame.Rect(screen_pos[0], screen_pos[1], self.grid.cell_size, self.grid.cell_size)
            highlight = pygame.Surface((self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA)
            highlight.fill((100, 255, 100, 80))
            screen.blit(highlight, rect)
            pygame.draw.rect(screen, (50, 255, 50), rect, 3)
        
        # Enemigos marcados
        for enemy in self.dash_targets:
            screen_pos = self.grid.get_screen_position(enemy.position)
            center = (screen_pos[0] + self.grid.cell_size // 2, screen_pos[1] + self.grid.cell_size // 2)
            pygame.draw.circle(screen, (255, 50, 50), center, 25, 4)
            
            damage = int(self.entity.stats['attack'] * 0.1)
            font = pygame.font.SysFont(None, 20)
            screen.blit(font.render(f"-{damage}", True, (255, 100, 100)), 
                       (center[0] - 10, center[1] - 35))
            screen.blit(font.render("EMBESTIDA", True, (255, 100, 100)), 
                       (center[0] - 30, center[1] + 20))
    
    def cancel(self):
        """Cancela el movimiento en curso"""
        if self.is_active:
            print("❌ Movimiento cancelado")
            self.reset()
    
    def get_state_info(self) -> dict:
        """Retorna información del estado actual"""
        return {
            'is_active': self.is_active,
            'entity': self.entity.name if self.entity else None,
            'path_length': len(self.movement_path),
            'dash_targets': len(self.dash_targets),
            'movement_range': self.movement_range
        }