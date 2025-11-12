import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.services.route_system import MovementRoute
## Eliminada importación circular de MovementVisualizer
from .rendering_service import RenderingService
from .action_menu import ActionMenu
from .game_states import GameState, GameContext

class EnhancedRenderingService(RenderingService):
    """Servicio de renderizado extendido con soporte para estados del juego"""

    def __init__(self, screen_width: int = None, screen_height: int = None):
        # Si no se especifica, usar pantalla completa
        pygame.init()
        info = pygame.display.Info()
        screen_width = screen_width or info.current_w
        screen_height = screen_height or info.current_h
        
        # Grid size fijo para laboratorio
        self.grid_size = (16, 12)
        
        # Calcular cell_size para que ocupe el 80% de la pantalla
        grid_area_w = int(screen_width * 0.8)
        grid_area_h = int(screen_height * 0.8)
        self.cell_size = min(
            grid_area_w // self.grid_size[0],
            grid_area_h // self.grid_size[1]
        )
        
        # Offset para centrar el grid
        self.grid_offset = (
            (screen_width - self.cell_size * self.grid_size[0]) // 2,
            (screen_height - self.cell_size * self.grid_size[1]) // 2
        )
        
        super().__init__(screen_width, screen_height)
        
        # Inicializar MovementVisualizer con los parámetros CORRECTOS
        self.movement_visualizer = MovementVisualizer(
            self.grid_offset, self.cell_size, self.grid_size
        )
        self.current_route: Optional[MovementRoute] = None
        self.action_menu: Optional[ActionMenu] = None
        self.game_context: Optional[GameContext] = None
        
        # Sistema de cámara
        self.camera_offset = [0, 0]
        self.camera_speed = 40
        
        self.update_visualizer_params()

    def update_visualizer_params(self):
        """Sincroniza los parámetros del visualizador con el grid actual"""
        self.movement_visualizer.grid_offset = self.grid_offset
        self.movement_visualizer.cell_size = self.cell_size
        self.movement_visualizer.grid_size = self.grid_size

    def _get_cell_rect(self, position: Position) -> pygame.Rect:
        """Calcula el rectángulo de una celda considerando la cámara"""
        return pygame.Rect(
            self.grid_offset[0] + position.x * self.cell_size - self.camera_offset[0],
            self.grid_offset[1] + position.y * self.cell_size - self.camera_offset[1],
            self.cell_size, self.cell_size
        )

    def _get_cell_center(self, position: Position) -> tuple:
        """Calcula el centro de una celda considerando la cámara"""
        cell_rect = self._get_cell_rect(position)
        return (
            cell_rect.x + self.cell_size // 2,
            cell_rect.y + self.cell_size // 2
        )

    def render_battle(self, battle, game_context: GameContext, valid_moves: List[Position] = None) -> None:
        self.screen.fill(self.colors["background"])
        
        # Debug: mostrar área del grid
        grid_rect = pygame.Rect(
            self.grid_offset[0] - self.camera_offset[0],
            self.grid_offset[1] - self.camera_offset[1],
            self.cell_size * self.grid_size[0],
            self.cell_size * self.grid_size[1]
        )
        pygame.draw.rect(self.screen, (40, 40, 80), grid_rect, 2)

        self.game_context = game_context
        
        # Renderizar componentes en orden correcto
        self._render_grid()
        self._render_valid_moves(valid_moves)
        
        for obstacle in battle._obstacles:
            self._render_obstacle(obstacle)
            
        # Renderizar rutas PRIMERO para que queden detrás de las entidades
        if (game_context.current_state == GameState.TRACING_ROUTE and 
            game_context.current_route is not None):
            selected_entity = battle.get_entity(game_context.selected_entity_id)
            if selected_entity:
                self._render_route_debug(selected_entity.position, game_context.current_route, game_context)
        
        # Luego renderizar entidades
        for entity in battle._entities.values():
            is_selected = entity.id == game_context.selected_entity_id
            is_marked_for_dash = entity.position in getattr(game_context, 'dash_anchors', [])
            self._render_entity(entity, is_selected, is_marked_for_dash)

        # Renderizar menú de acciones si es necesario
        if (game_context.current_state == GameState.ENTITY_SELECTED and 
            self.action_menu is not None):
            self.action_menu.draw(self.screen)
            
        self._render_state_info(game_context)
        self._render_ui(battle)
        
        pygame.display.flip()
        self.clock.tick(60)

    def _render_route_debug(self, start_pos: Position, route: MovementRoute, game_context: GameContext):
        """Renderiza la ruta con debug visual para asegurar alineación"""
        # Dibujar línea de ruta
        all_points = [self._get_cell_center(start_pos)]
        for pos in route.path:
            all_points.append(self._get_cell_center(pos))
        
        if len(all_points) > 1:
            pygame.draw.lines(self.screen, (0, 255, 0), False, all_points, 3)
        
        # Puntos de debug numerados
        font = pygame.font.Font(None, 20)
        
        # Punto de inicio (azul)
        start_center = self._get_cell_center(start_pos)
        pygame.draw.circle(self.screen, (0, 0, 255), start_center, 8)
        start_text = font.render("S", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=start_center)
        self.screen.blit(start_text, start_rect)
        
        # Puntos intermedios (verde)
        for i, pos in enumerate(route.path):
            center = self._get_cell_center(pos)
            pygame.draw.circle(self.screen, (0, 255, 0), center, 6)
            text = font.render(str(i+1), True, (0, 0, 0))
            text_rect = text.get_rect(center=center)
            self.screen.blit(text, text_rect)
        
        # Punto final (rojo)
        if route.path:
            end_center = self._get_cell_center(route.path[-1])
            pygame.draw.circle(self.screen, (255, 0, 0), end_center, 8)
            end_text = font.render("E", True, (255, 255, 255))
            end_rect = end_text.get_rect(center=end_center)
            self.screen.blit(end_text, end_rect)

    def _render_entity(self, entity, is_selected: bool = False, is_marked_for_dash: bool = False):
        """Renderiza una entidad correctamente alineada con el grid"""
        pos = entity.position
        team = entity.team
        
        # Obtener posición centrada en la celda
        screen_x, screen_y = self._get_cell_center(pos)

        # Color según equipo
        if team == "player" or (hasattr(team, 'value') and team.value == "player"):
            color = (30, 144, 255)  # Azul para jugador
        else:
            color = self.colors["enemy"]  # Rojo para enemigo

        # Dibujar entidad
        radius = self.cell_size // 3
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
        
        # Resaltar selección
        if is_selected:
            pygame.draw.circle(self.screen, self.colors["selected"], 
                             (screen_x, screen_y), radius + 4, 3)
        
        # Resaltar para embestida
        if is_marked_for_dash:
            pygame.draw.circle(self.screen, (255, 50, 50), 
                             (screen_x, screen_y), radius + 8, 3)
        
        # Barra de salud
        health_percent = entity.stats.current_hp / entity.stats.max_hp
        bar_width = self.cell_size - 10
        bar_height = 6
        
        cell_rect = self._get_cell_rect(pos)
        bar_x = cell_rect.x + (self.cell_size - bar_width) // 2
        bar_y = cell_rect.y + 4
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Barra de salud
        pygame.draw.rect(self.screen, self.colors["health_bar"], 
                        (bar_x, bar_y, int(bar_width * health_percent), bar_height))
        
        # Nombre de la entidad
        name_surface = self.font.render(entity.name, True, self.colors["text"])
        name_rect = name_surface.get_rect(center=(screen_x, bar_y - 10))
        self.screen.blit(name_surface, name_rect)

    def _render_obstacle(self, position: Position) -> None:
        """Renderiza un obstáculo centrado en la celda"""
        screen_x, screen_y = self._get_cell_center(position)
        size = self.cell_size - 14
        rect = pygame.Rect(
            screen_x - size // 2,
            screen_y - size // 2,
            size,
            size
        )
        pygame.draw.rect(self.screen, self.colors["obstacle"], rect)

    def _render_grid(self) -> None:
        """Renderiza el grid táctico"""
        # Dibujar líneas verticales
        for x in range(self.grid_size[0] + 1):
            start_x = self.grid_offset[0] + x * self.cell_size - self.camera_offset[0]
            pygame.draw.line(
                self.screen, self.colors["grid"],
                (start_x, self.grid_offset[1] - self.camera_offset[1]),
                (start_x, self.grid_offset[1] + self.grid_size[1] * self.cell_size - self.camera_offset[1])
            )
        
        # Dibujar líneas horizontales
        for y in range(self.grid_size[1] + 1):
            start_y = self.grid_offset[1] + y * self.cell_size - self.camera_offset[1]
            pygame.draw.line(
                self.screen, self.colors["grid"],
                (self.grid_offset[0] - self.camera_offset[0], start_y),
                (self.grid_offset[0] + self.grid_size[0] * self.cell_size - self.camera_offset[0], start_y)
            )

    def _render_valid_moves(self, valid_moves: List[Position]) -> None:
        """Renderiza las posiciones de movimiento válidas"""
        if not valid_moves:
            return
            
        for pos in valid_moves:
            cell_rect = self._get_cell_rect(pos)
            # Crear superficie semitransparente
            highlight = pygame.Surface((self.cell_size - 8, self.cell_size - 8), pygame.SRCALPHA)
            highlight.fill((0, 255, 0, 64))  # Verde semitransparente
            self.screen.blit(highlight, (cell_rect.x + 4, cell_rect.y + 4))

    def _render_state_info(self, game_context: GameContext):
        """Renderiza información del estado actual del juego"""
        state_info = {
            GameState.IDLE: "💤 IDLE - Selecciona una entidad",
            GameState.ENTITY_SELECTED: "📋 ENTIDAD SELECCIONADA - Elige una acción",
            GameState.TRACING_ROUTE: "🛣️ TRAZANDO RUTA - Arrastra para mover, click en enemigos para embestida",
            GameState.TARGETING_ABILITY: "🎯 SELECCIONANDO OBJETIVO - Click en objetivo",
            GameState.AWAITING_CONFIRMATION: "⏳ CONFIRMACIÓN - Confirmando acción..."
        }
        
        state_text = state_info.get(game_context.current_state, "Estado desconocido")
        state_surface = self.font.render(state_text, True, (255, 255, 255))
        state_rect = state_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
        self.screen.blit(state_surface, state_rect)

    def move_camera(self, dx: int, dy: int):
        """Desplaza la cámara con límites"""
        max_offset_x = max(0, self.grid_size[0] * self.cell_size - self.screen_width)
        max_offset_y = max(0, self.grid_size[1] * self.cell_size - self.screen_height)
        
        self.camera_offset[0] = max(0, min(self.camera_offset[0] + dx, max_offset_x))
        self.camera_offset[1] = max(0, min(self.camera_offset[1] + dy, max_offset_y))

    def update_route_preview(self, route: Optional[MovementRoute]) -> None:
        """Actualiza la ruta que se está previsualizando"""
        self.current_route = route

    def set_action_menu(self, action_menu: Optional[ActionMenu]) -> None:
        """Establece el menú de acciones actual"""
        self.action_menu = action_menu

    def _render_ui(self, battle) -> None:
        """Renderiza la interfaz de usuario"""
        # Información del turno
        turn_color = self.colors["player_turn"] if battle.current_turn == "player" else self.colors["enemy_turn"]
        turn_text = f"TURNO: {'JUGADOR' if battle.current_turn == 'player' else 'ENEMIGO'}"
        turn_surface = self.big_font.render(turn_text, True, turn_color)
        turn_rect = turn_surface.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(turn_surface, turn_rect)
        
        # Información de la batalla
        info_lines = [
            f"Acciones: {battle.actions_remaining}/3",
            f"Turno: {battle.turn_count}",
            f"Jugadores: {len(battle.get_player_entities())} | Enemigos: {len(battle.get_enemy_entities())}"
        ]
        
        for i, line in enumerate(info_lines):
            info_surface = self.font.render(line, True, self.colors["text"])
            info_rect = info_surface.get_rect(topleft=(10, 10 + i * 25))
            self.screen.blit(info_surface, info_rect)
        
        # Controles
        controls = [
            "CONTROLES:",
            "CLICK - Seleccionar/Mover entidad", 
            "ESPACIO - Terminar turno",
            "R - Reiniciar batalla",
            "ESC - Salir"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, self.colors["text"])
            control_rect = control_surface.get_rect(topright=(self.screen_width - 10, 10 + i * 25))
            self.screen.blit(control_surface, control_rect)