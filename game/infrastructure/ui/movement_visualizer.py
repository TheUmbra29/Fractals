import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.entities.battle_entity import BattleEntity
from core.domain.services.route_system import MovementRoute
from core.domain.entities.value_objects.entity_id import EntityId

class MovementVisualizer:
    """Renderiza rutas dinámicas con soporte para embestidas manuales"""

    def __init__(self, grid_offset: tuple, cell_size: int, grid_size: tuple):
        self.grid_offset = grid_offset
        self.cell_size = cell_size
        self.grid_size = grid_size
        
        # Colores mejorados
        self.colors = {
            "valid_route": (100, 200, 100),      # Verde
            "invalid_route": (255, 165, 0),      # Naranja  
            "dash_target": (255, 50, 50),        # Rojo para enemigos detectados
            "marked_dash_target": (255, 0, 0),   # Rojo intenso para marcados manualmente
            "route_line": (255, 255, 255, 180),  # Línea blanca semitransparente
            "path_node": (200, 230, 255, 150),   # Nodos de ruta azul claro
        }

    def render_route(self, screen: pygame.Surface, route: Optional[MovementRoute], 
                    current_position: Position, is_dragging: bool = False,
                    marked_dash_targets: List[EntityId] = None) -> None:
        """Renderiza una ruta completa con conexiones de embestidas"""
        if not route or not route.path:
            return
            
        if marked_dash_targets is None:
            marked_dash_targets = []
            
        route_color = self.colors["valid_route"] if route.is_valid else self.colors["invalid_route"]
        
        # Renderizar línea de ruta
        self._render_route_line(screen, current_position, route.path, route_color)
        
        # Renderizar nodos del camino
        self._render_path_nodes(screen, route.path)
        
        # ✅ NUEVO: Renderizar conexiones de embestidas
        if route.dash_targets:
            self._render_dash_connections(screen, route.dash_targets, route.path, route_color)
        
        # Renderizar enemigos para embestida
        self._render_dash_targets(screen, route.dash_targets, marked_dash_targets, route_color)
        
        # Renderizar información de daño
        if route.dash_targets:
            self._render_dash_damage_info(screen, route, marked_dash_targets)

    def _render_route_line(self, screen: pygame.Surface, start_pos: Position, 
                          path: List[Position], color: tuple) -> None:
        """Renderiza la línea continua de la ruta"""
        if not path:
            return
            
        # Convertir posiciones a coordenadas de pantalla
        screen_points = []
        
        # Punto inicial (posición actual de la entidad)
        start_screen = self._position_to_screen(start_pos)
        screen_points.append(start_screen)
        
        # Puntos de la ruta
        for pos in path:
            screen_pos = self._position_to_screen(pos)
            screen_points.append(screen_pos)
        
        # Dibujar líneas conectadas
        if len(screen_points) > 1:
            pygame.draw.lines(screen, color, False, screen_points, 3)
            
            # Dibujar punto final más grande
            end_pos = screen_points[-1]
            pygame.draw.circle(screen, color, end_pos, 8)

    def _render_path_nodes(self, screen: pygame.Surface, path: List[Position]) -> None:
        """Renderiza nodos individuales del camino"""
        for i, pos in enumerate(path):
            screen_pos = self._position_to_screen(pos)
            
            # Dibujar círculo en cada nodo (excepto el último que ya tiene uno grande)
            if i < len(path) - 1:
                pygame.draw.circle(screen, self.colors["path_node"], screen_pos, 5)
                
                # Número de paso (opcional)
                font = pygame.font.Font(None, 20)
                text = font.render(str(i+1), True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 15))
                screen.blit(text, text_rect)

    def _render_dash_targets(self, screen: pygame.Surface, dash_targets: List[BattleEntity], 
                           marked_dash_targets: List[EntityId], route_color: tuple) -> None:
        """Renderiza enemigos para embestida diferenciando marcados manualmente"""
        for target in dash_targets:
            target_screen = self._position_to_screen(target.position)
            
            # Determinar color y tamaño según si está marcado manualmente
            if target.id in marked_dash_targets:
                color = self.colors["marked_dash_target"]  # Rojo intenso
                radius = self.cell_size // 2 + 10
                pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500  # Efecto pulsante
                radius = int(radius * (0.8 + pulse * 0.2))
            else:
                color = self.colors["dash_target"]  # Rojo normal
                radius = self.cell_size // 2 + 5
            
            # Círculo alrededor del enemigo
            pygame.draw.circle(screen, color, target_screen, radius, 3)
            
            # Línea conectada desde la ruta al enemigo
            # Corregido: pasar la ruta de posiciones, no la lista de entidades
            route_positions = [t.position if hasattr(t, 'position') else t for t in dash_targets]
            closest_route_point = self._find_closest_route_point(target.position, route_positions)
            if closest_route_point:
                route_screen = self._position_to_screen(closest_route_point)
                pygame.draw.line(screen, color, route_screen, target_screen, 2)
            
            # Icono de espada (más grande si está marcado)
            self._render_sword_icon(screen, target_screen, target.id in marked_dash_targets)

    def _render_dash_damage_info(self, screen: pygame.Surface, route: MovementRoute, 
                               marked_dash_targets: List[EntityId]) -> None:
        """Renderiza tooltip con información de daño diferenciando embestidas manuales"""
        if not route.dash_targets:
            return
            
        # Calcular daño de embestidas marcadas vs automáticas
        auto_dash_count = len([t for t in route.dash_targets if t.id not in marked_dash_targets])
        manual_dash_count = len([t for t in route.dash_targets if t.id in marked_dash_targets])
        total_damage = len(route.dash_targets) * 15
        
        # Posicionar en la parte superior de la pantalla
        info_x, info_y = 400, 30
        
        # Fondo semitransparente
        info_bg = pygame.Surface((250, 80), pygame.SRCALPHA)
        info_bg.fill((40, 40, 60, 200))
        screen.blit(info_bg, (info_x - 10, info_y - 10))
        
        # Texto de información
        font = pygame.font.Font(None, 22)
        
        if manual_dash_count > 0:
            manual_text = f"Embestidas MANUALES: {manual_dash_count}"
            manual_surface = font.render(manual_text, True, (255, 100, 100))
            screen.blit(manual_surface, (info_x, info_y))
            
        if auto_dash_count > 0:
            auto_text = f"Embestidas AUTOMÁTICAS: {auto_dash_count}"
            auto_surface = font.render(auto_text, True, (255, 200, 200))
            screen.blit(auto_surface, (info_x, info_y + 20))
        
        damage_text = f"Daño total: {total_damage}"
        damage_surface = font.render(damage_text, True, (255, 255, 255))
        screen.blit(damage_surface, (info_x, info_y + 45))

    def _render_sword_icon(self, screen: pygame.Surface, position: tuple, is_marked: bool = False):
        """Renderiza icono de espada (más grande si está marcado)"""
        x, y = position
        size_multiplier = 1.5 if is_marked else 1.0
        
        # Dibujar espada simple (triángulo)
        points = [
            (x, y - 8 * size_multiplier),                    # Punta
            (x - 4 * size_multiplier, y + 4 * size_multiplier),  # Base izquierda  
            (x + 4 * size_multiplier, y + 4 * size_multiplier)   # Base derecha
        ]
        
        color = (255, 255, 255) if is_marked else (200, 200, 200)
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (150, 150, 150), points, 1)

    def _position_to_screen(self, position: Position) -> tuple:
        """Convierte posición del grid a coordenadas de pantalla"""
        x = self.grid_offset[0] + position.x * self.cell_size + self.cell_size // 2
        y = self.grid_offset[1] + position.y * self.cell_size + self.cell_size // 2
        return (x, y)
    
    def _find_closest_route_point(self, target_pos: Position, route_path: List[Position]) -> Optional[Position]:
        """Encuentra el punto de ruta más cercano REALMENTE"""
        if not route_path:
            return None
            
        closest_point = None
        min_distance = float('inf')
        
        for route_pos in route_path:
            distance = target_pos.distance_to(route_pos)
            if distance < min_distance:
                min_distance = distance
                closest_point = route_pos
        
        # Solo retornar si está suficientemente cerca (ad-yacente)
        return closest_point if min_distance <= 1 else None

    def _render_dash_connections(self, screen: pygame.Surface, dash_targets: List[BattleEntity], 
                            route_path: List[Position], color: tuple):
        """Renderiza conexiones entre ruta y enemigos embestidos"""
        for target in dash_targets:
            closest_route_point = self._find_closest_route_point(target.position, route_path)
            if closest_route_point:
                target_screen = self._position_to_screen(target.position)
                route_screen = self._position_to_screen(closest_route_point)
                
                # Línea punteada para conexión
                self._draw_dashed_line(screen, color, route_screen, target_screen, dash_length=8)
                
                # Punto de conexión en la ruta
                pygame.draw.circle(screen, color, route_screen, 6, 2)

    def _draw_dashed_line(self, screen: pygame.Surface, color: tuple, start: tuple, end: tuple, dash_length: int = 5):
        """Dibuja una línea punteada"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = max(1, (dx**2 + dy**2)**0.5)
        dashes = int(distance / dash_length)
        
        for i in range(dashes):
            start_percent = i / dashes
            end_percent = (i + 0.5) / dashes  # Mitad del dash para crear el espacio
            
            start_x = start[0] + dx * start_percent
            start_y = start[1] + dy * start_percent
            end_x = start[0] + dx * end_percent  
            end_y = start[1] + dy * end_percent
            
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 2)