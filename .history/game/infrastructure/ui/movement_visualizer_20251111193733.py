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
            "valid_route": (0, 255, 0),      # Verde puro
            "invalid_route": (255, 165, 0),      # Naranja  
            "dash_target": (255, 50, 50),        # Rojo para enemigos detectados
            "marked_dash_target": (255, 0, 0),   # Rojo intenso para marcados manualmente
            "route_line": (0, 255, 0),  # Línea verde principal
            "path_node": (200, 230, 255, 150),   # Nodos de ruta azul claro
        }

    def render_route(self, screen: pygame.Surface, route: Optional[MovementRoute], 
                    current_position: Position, is_dragging: bool = False,
                    dash_anchors: List[Position] = None, camera_offset=None) -> None:
        """Renderiza ruta con puntos de anclaje especiales y soporte de cámara"""
        if not route or not route.path:
            return
        
        if dash_anchors is None:
            dash_anchors = []
        
        if camera_offset is None:
            camera_offset = [0, 0]
        
        route_color = self.colors["valid_route"] if route.is_valid else self.colors["invalid_route"]
        
        # 1. Renderizar línea de ruta principal
        self._render_route_line(screen, current_position, route.path, route_color, camera_offset)
        
        # 2. Renderizar puntos de anclaje con numeración
        for i, anchor_pos in enumerate(dash_anchors):
            anchor_screen = self._position_to_screen(anchor_pos, camera_offset)
            
            # Círculo especial para anclajes
            pygame.draw.circle(screen, (255, 0, 0), anchor_screen, 12, 3)
            
            # Número de anclaje
            font = pygame.font.Font(None, 18)
            text = font.render(str(i+1), True, (255, 255, 255))
            text_rect = text.get_rect(center=anchor_screen)
            screen.blit(text, text_rect)
            
            # Icono de espada en anclajes
            self._render_sword_icon(screen, anchor_screen, is_anchor=True)

    def _render_route_line(self, screen: pygame.Surface, start_pos: Position, 
                          path: List[Position], color: tuple, camera_offset=None) -> None:
        """Renderiza la línea continua de la ruta centrada en cada celda"""
        if not path:
            return
        if camera_offset is None:
            camera_offset = [0, 0]
        screen_points = []
        # Refuerzo: el primer punto SIEMPRE es la posición inicial
        start_screen = self._position_to_screen(start_pos, camera_offset)
        start_center = (start_screen[0] + self.cell_size // 2, start_screen[1] + self.cell_size // 2)
        screen_points.append(start_center)
        for pos in path:
            screen_pos = self._position_to_screen(pos, camera_offset)
            center = (screen_pos[0] + self.cell_size // 2, screen_pos[1] + self.cell_size // 2)
            screen_points.append(center)
        if len(screen_points) > 1:
            pygame.draw.lines(screen, color, False, screen_points, 3)
            end_pos = screen_points[-1]
            pygame.draw.circle(screen, color, end_pos, 8)
        # Círculo azul de depuración sobre el primer punto
        pygame.draw.circle(screen, (0,0,255), start_center, 12)

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

    def _render_sword_icon(self, screen: pygame.Surface, position: tuple, is_anchor: bool = False):
        """Renderiza icono de espada (especial para anclajes)"""
        x, y = position
        size = 1.8 if is_anchor else 1.0  # Más grande para anclajes
        
        # Espada más detallada para anclajes
        points = [
            (x, y - 10 * size),                    # Punta
            (x - 3 * size, y - 3 * size),          # Guarda izquierda
            (x - 5 * size, y + 5 * size),          # Base izquierda  
            (x - 2 * size, y + 6 * size),          # Empuñadura izquierda
            (x + 2 * size, y + 6 * size),          # Empuñadura derecha
            (x + 5 * size, y + 5 * size),          # Base derecha
            (x + 3 * size, y - 3 * size),          # Guarda derecha
        ]
        
        color = (255, 255, 0) if is_anchor else (255, 255, 255)  # Amarillo para anclajes
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (200, 200, 0), points, 1)

    def _position_to_screen(self, position: Position, camera_offset=None) -> tuple:
        """Convierte posición del grid a coordenadas de pantalla (misma fórmula que entidades y grid)"""
        if camera_offset is None:
            camera_offset = [0, 0]
        x = self.grid_offset[0] + position.x * self.cell_size - camera_offset[0]
        y = self.grid_offset[1] + position.y * self.cell_size - camera_offset[1]
    # print(f"[POS DEBUG] Grid: {position} -> Pantalla: ({x}, {y}) | Offset: {self.grid_offset} | Cell: {self.cell_size} | Cam: {camera_offset}")
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