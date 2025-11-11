import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.services.route_system import MovementRoute
from .movement_visualizer import MovementVisualizer
from .rendering_service import RenderingService
from .action_menu import ActionMenu
from .game_states import GameState, GameContext

class EnhancedRenderingService(RenderingService):
    """Servicio de renderizado extendido con soporte para estados del juego"""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        super().__init__(screen_width, screen_height)
        self.movement_visualizer = MovementVisualizer(
            self.grid_offset, self.cell_size, self.grid_size
        )
        self.current_route: Optional[MovementRoute] = None
        self.action_menu: Optional[ActionMenu] = None
        self.game_context: Optional[GameContext] = None

    def render_battle(self, battle, game_context: GameContext, valid_moves: List[Position] = None) -> None:
        """Renderiza la batalla considerando el estado actual del juego"""
        self.game_context = game_context
        self.screen.fill(self.colors["background"])
        
        # Renderizar elementos básicos
        self._render_grid()
        self._render_valid_moves(valid_moves)
        
        for obstacle in battle._obstacles:
            self._render_obstacle(obstacle)
        
        # Renderizar entidades con marcado especial para embestidas
        for entity in battle._entities.values():
            is_selected = entity.id == game_context.selected_entity_id
            is_marked_for_dash = entity.position in getattr(game_context, 'dash_anchors', [])
            self._render_entity(entity, is_selected, is_marked_for_dash)
        
        # Renderizar ruta de movimiento si estamos en modo trazado
        if (game_context.current_state == GameState.TRACING_ROUTE and 
            game_context.current_route is not None):
            
            selected_entity = battle.get_entity(game_context.selected_entity_id)
            if selected_entity:
                self.movement_visualizer.render_route(
                    self.screen, 
                    game_context.current_route, 
                    selected_entity.position, 
                    is_dragging=False,
                    dash_anchors=getattr(game_context, 'dash_anchors', [])
                )
        
        # Renderizar menú de acciones si hay entidad seleccionada
        if (game_context.current_state == GameState.ENTITY_SELECTED and 
            self.action_menu is not None):
            self.action_menu.draw(self.screen)
        
        # Renderizar información de estado actual
        self._render_state_info(game_context)
        
        self._render_ui(battle)
        
        pygame.display.flip()
        self.clock.tick(60)

    def _render_entity(self, entity, is_selected: bool = False, is_marked_for_dash: bool = False):
        """Renderiza una entidad con marcado especial para embestidas"""
        pos = entity.position
        team = entity.team

        screen_x = self.grid_offset[0] + pos.x * self.cell_size
        screen_y = self.grid_offset[1] + pos.y * self.cell_size

        # Color según equipo
        if team == "player" or (hasattr(team, 'value') and team.value == "player"):
            color = (30, 144, 255)
        elif team == "enemy" or (hasattr(team, 'value') and team.value == "enemy"):
            color = self.colors["enemy"]
        else:
            color = self.colors["enemy"]

        # Dibujar entidad
        radius = self.cell_size // 3
        pygame.draw.circle(self.screen, color, (screen_x + self.cell_size//2, screen_y + self.cell_size//2), radius)
        
        # Resaltar si está seleccionada
        if is_selected:
            pygame.draw.circle(self.screen, self.colors["selected"], 
                             (screen_x + self.cell_size//2, screen_y + self.cell_size//2), 
                             radius + 4, 3)  # Borde amarillo más grueso
        
        # Resaltar si está marcada para embestida
        if is_marked_for_dash:
            pygame.draw.circle(self.screen, (255, 50, 50),  # Rojo brillante
                             (screen_x + self.cell_size//2, screen_y + self.cell_size//2), 
                             radius + 8, 3)  # Círculo rojo exterior
        
        # Barra de salud
        health_percent = entity.stats.current_hp / entity.stats.max_hp
        bar_width = self.cell_size - 10
        bar_height = 6
        
        # Fondo barra
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (screen_x + 5, screen_y - 10, bar_width, bar_height))
        # Salud actual
        pygame.draw.rect(self.screen, self.colors["health_bar"], 
                        (screen_x + 5, screen_y - 10, int(bar_width * health_percent), bar_height))
        
        # Nombre de la entidad
        name_surface = self.font.render(entity.name, True, self.colors["text"])
        name_rect = name_surface.get_rect(center=(screen_x + self.cell_size//2, screen_y - 25))
        self.screen.blit(name_surface, name_rect)

    def _render_state_info(self, game_context: GameContext):
        """Renderiza información del estado actual del juego"""
        state_info = {
            GameState.IDLE: "💤 IDLE - Selecciona una entidad",
            GameState.ENTITY_SELECTED: "📋 ENTIDAD SELECCIONADA - Elige una acción",
            GameState.TRACING_ROUTE: "🛣️ TRAZANDO RUTA - Mueve el cursor, click en enemigos para embestida",
            GameState.TARGETING_ABILITY: "🎯 SELECCIONANDO OBJETIVO - Click en objetivo",
            GameState.AWAITING_CONFIRMATION: "⏳ CONFIRMACIÓN - Confirmando acción..."
        }
        
        state_text = state_info.get(game_context.current_state, "Estado desconocido")
        state_surface = self.font.render(state_text, True, (255, 255, 255))
        self.screen.blit(state_surface, (20, self.screen_height - 40))
        
        # Información adicional para modo trazado
        if (game_context.current_state == GameState.TRACING_ROUTE and 
            getattr(game_context, 'dash_anchors', [])):
            dash_info = f"Embestidas marcadas: {len(game_context.dash_anchors)}"
            dash_surface = self.font.render(dash_info, True, (255, 200, 200))
            self.screen.blit(dash_surface, (300, self.screen_height - 40))

    def update_route_preview(self, route: Optional[MovementRoute]) -> None:
        """Actualiza la ruta que se está previsualizando"""
        self.current_route = route

    def set_action_menu(self, action_menu: Optional[ActionMenu]) -> None:
        """Establece el menú de acciones actual"""
        self.action_menu = action_menu