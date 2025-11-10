import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.entities.battle_entity import BattleEntity
from core.domain.services.route_system import MovementRoute

class MovementVisualizer:
    """Renderiza rutas dinámicas y feedback visual para el movimiento"""
    
    def __init__(self, grid_offset: tuple, cell_size: int, grid_size: tuple):
        self.grid_offset = grid_offset
        self.cell_size = cell_size
        self.grid_size = grid_size
        
        # Colores según especificaciones
        self.colors = {
            "valid_route": (100, 200, 100),      # Verde
            "invalid_route": (255, 165, 0),      # Naranja  
            "dash_target": (255, 50, 50),        # Rojo para enemigos marcados
            "route_line": (255, 255, 255, 180),  # Línea blanca semitransparente
            "path_node": (200, 230, 255, 150),   # Nodos de ruta azul claro
        }
    
    def render_route(self, screen: pygame.Surface, route: Optional[MovementRoute], 
                    current_position: Position, is_dragging: bool = False) -> None:
        """Renderiza una ruta completa con todos sus elementos"""
        if not route or not route.path:
            return
            
        # Determinar color basado en validez
        route_color = self.colors["valid_route"] if route.is_valid else self.colors["invalid_route"]
        
        # Renderizar línea de ruta
        self._render_route_line(screen, current_position, route.path, route_color)
        
        # Renderizar nodos del camino
        self._render_path_nodes(screen, route.path)
        
        # Renderizar enemigos marcados para embestida
        self._render_dash_targets(screen, route.dash_targets, route_color)
        
        # Renderizar información de daño de embestida
        if route.dash_targets:
            self._render_dash_damage_info(screen, route)
    
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
            
            # Dibujar círculo en cada nodo
            pygame.draw.circle(screen, self.colors["path_node"], screen_pos, 5)
            
            # Número de paso (opcional)
            if i < len(path) - 1:  # No mostrar número en el último nodo
                font = pygame.font.Font(None, 20)
                text = font.render(str(i+1), True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 15))
                screen.blit(text, text_rect)
    
    def _render_dash_targets(self, screen: pygame.Surface, dash_targets: List[BattleEntity], route_color: tuple) -> None:
        """Renderiza enemigos marcados para embestida con círculos rojos conectados"""
        for target in dash_targets:
            target_screen = self._position_to_screen(target.position)
            
            # Círculo rojo pulsante alrededor del enemigo
            radius = self.cell_size // 2 + 5
            pygame.draw.circle(screen, self.colors["dash_target"], target_screen, radius, 3)
            
            # Línea conectada desde la ruta al enemigo
            closest_route_point = self._find_closest_route_point(target.position, dash_targets)
            if closest_route_point:
                route_screen = self._position_to_screen(closest_route_point)
                pygame.draw.line(screen, self.colors["dash_target"], route_screen, target_screen, 2)
                
            # Icono de espada pequeño
            self._render_sword_icon(screen, target_screen)
    
    def _render_dash_damage_info(self, screen: pygame.Surface, route: MovementRoute) -> None:
        """Renderiza tooltip con información de daño de embestida"""
        if not route.dash_targets:
            return
            
        # Posicionar en la parte superior de la pantalla
        info_x, info_y = 400, 50
        
        # Fondo semitransparente
        info_bg = pygame.Surface((200, 60), pygame.SRCALPHA)
        info_bg.fill((40, 40, 60, 200))
        screen.blit(info_bg, (info_x - 10, info_y - 10))
        
        # Texto de daño
        font = pygame.font.Font(None, 24)
        damage_text = f"Embestidas: {len(route.dash_targets)}"
        damage_surface = font.render(damage_text, True, (255, 255, 255))
        screen.blit(damage_surface, (info_x, info_y))
        
        damage_calc = f"Daño total: 15 × {len(route.dash_targets)} = {route.dash_damage}"
        calc_surface = font.render(damage_calc, True, (255, 200, 200))
        screen.blit(calc_surface, (info_x, info_y + 25))
    
    def _render_sword_icon(self, screen: pygame.Surface, position: tuple) -> None:
        """Renderiza un pequeño icono de espada"""
        x, y = position
        # Dibujar espada simple (triángulo)
        points = [
            (x, y - 8),      # Punta
            (x - 4, y + 4),  # Base izquierda  
            (x + 4, y + 4)   # Base derecha
        ]
        pygame.draw.polygon(screen, (255, 255, 255), points)
        pygame.draw.polygon(screen, (200, 200, 200), points, 1)
    
    def _position_to_screen(self, position: Position) -> tuple:
        """Convierte posición del grid a coordenadas de pantalla"""
        x = self.grid_offset[0] + position.x * self.cell_size + self.cell_size // 2
        y = self.grid_offset[1] + position.y * self.cell_size + self.cell_size // 2
        return (x, y)
    
    def _find_closest_route_point(self, target_pos: Position, dash_targets: List[BattleEntity]) -> Optional[Position]:
        """Encuentra el punto de ruta más cercano a un enemigo"""
        # Implementación simplificada - en una versión completa usaríamos la ruta real
        return target_pos