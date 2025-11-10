# infrastructure/ui/enhanced_rendering_service.py
import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.services.route_system import MovementRoute
from .movement_visualizer import MovementVisualizer
from .rendering_service import RenderingService

class EnhancedRenderingService(RenderingService):
    """Extiende el servicio de renderizado con funcionalidades de movimiento"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        super().__init__(screen_width, screen_height)
        self.movement_visualizer = MovementVisualizer(
            self.grid_offset, self.cell_size, self.grid_size
        )
        self.current_route: Optional[MovementRoute] = None
        self.is_dragging = False
        self.drag_start_pos = None

    def render_battle(self, battle, selected_entity_id: Optional[str] = None, 
                    valid_moves: List[Position] = None) -> None:
        """Renderiza la batalla con rutas de movimiento"""
        self.screen.fill(self.colors["background"])
        
        # Renderizar elementos básicos
        self._render_grid()
        
        for obstacle in battle._obstacles:
            self._render_obstacle(obstacle)
        
        for entity in battle._entities.values():
            is_selected = entity.id == selected_entity_id
            self._render_entity(entity, is_selected)
        
        # Renderizar ruta de movimiento SI existe
        if self.current_route and selected_entity_id:
            selected_entity = None
            for entity in battle._entities.values():
                if entity.id == selected_entity_id:
                    selected_entity = entity
                    break
                    
            if selected_entity:
                self.movement_visualizer.render_route(
                    self.screen, self.current_route, 
                    selected_entity.position, self.is_dragging
                )
        
        self._render_ui(battle)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def update_route_preview(self, route: Optional[MovementRoute], is_dragging: bool = False) -> None:
        """Actualiza la ruta que se está previsualizando"""
        self.current_route = route
        self.is_dragging = is_dragging
    
    def start_drag(self, start_position: Position) -> None:
        """Inicia el arrastre para movimiento"""
        self.drag_start_pos = start_position
        self.is_dragging = True
    
    def end_drag(self) -> None:
        """Termina el arrastre"""
        self.is_dragging = False
        self.drag_start_pos = None