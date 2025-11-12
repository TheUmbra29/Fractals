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

    def __init__(self, screen_width: int = None, screen_height: int = None):
        # Si no se especifica, usar pantalla completa
        pygame.init()
        info = pygame.display.Info()
        screen_width = screen_width or info.current_w
        screen_height = screen_height or info.current_h
        # Forzar grid_size a laboratorio
        self.grid_size = (16, 12)
        # El grid ocupará el 80% del ancho/alto de la pantalla
        grid_area_w = int(screen_width * 0.8)
        grid_area_h = int(screen_height * 0.8)
        self.cell_size = min(
            grid_area_w // self.grid_size[0],
            grid_area_h // self.grid_size[1]
        )
        # Offset para centrar el grid en pantalla
        self.grid_offset = (
            (screen_width - self.cell_size * self.grid_size[0]) // 2,
            (screen_height - self.cell_size * self.grid_size[1]) // 2
        )
        super().__init__(screen_width, screen_height)
        self.movement_visualizer = MovementVisualizer(
            self.grid_offset, self.cell_size, self.grid_size
        )
        self.current_route: Optional[MovementRoute] = None
        self.action_menu: Optional[ActionMenu] = None
        self.game_context: Optional[GameContext] = None
        # Offset de cámara (en píxeles)
        self.camera_offset = [0, 0]
        self.camera_speed = 40  # píxeles por movimiento
        # Sincronizar visualizador tras inicialización
        self.update_visualizer_params()

    def update_visualizer_params(self):
        """Sincroniza los parámetros del visualizador con el grid actual"""
        self.movement_visualizer.grid_offset = self.grid_offset
        self.movement_visualizer.cell_size = self.cell_size
        self.movement_visualizer.grid_size = self.grid_size

    def render_battle(self, battle, game_context: GameContext, valid_moves: List[Position] = None) -> None:
        self.screen.fill(self.colors["background"])
        # Fondo de depuración: rectángulo donde debería estar el grid
        grid_rect = pygame.Rect(
            self.grid_offset[0], self.grid_offset[1],
            self.cell_size * self.grid_size[0], self.cell_size * self.grid_size[1]
        )
        pygame.draw.rect(self.screen, (40, 40, 80), grid_rect, 2)
        # Celdas de esquina para comparar
        cell_00 = pygame.Rect(
            self.grid_offset[0], self.grid_offset[1], self.cell_size, self.cell_size)
        cell_max = pygame.Rect(
            self.grid_offset[0] + (self.grid_size[0]-1)*self.cell_size,
            self.grid_offset[1] + (self.grid_size[1]-1)*self.cell_size,
            self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, (0,255,0), cell_00, 3)
        pygame.draw.rect(self.screen, (255,0,0), cell_max, 3)
        """Renderiza la batalla considerando el estado actual del juego"""
        self.game_context = game_context
        self._render_grid()
        self._render_valid_moves(valid_moves)
        for obstacle in battle._obstacles:
            self._render_obstacle(obstacle)
        for entity in battle._entities.values():
            is_selected = entity.id == game_context.selected_entity_id
            is_marked_for_dash = entity.position in getattr(game_context, 'dash_anchors', [])
            # Calcular la posición visual exacta de la celda lógica
            cell_rect = pygame.Rect(
                self.grid_offset[0] + entity.position.x * self.cell_size,
                self.grid_offset[1] + entity.position.y * self.cell_size,
                self.cell_size, self.cell_size
            )
            # Resaltar Ricchard en su celda lógica
            if getattr(entity, 'name', '') == 'Ricchard':
                pygame.draw.rect(self.screen, (0, 255, 0), cell_rect, 6)
                font = pygame.font.Font(None, 26)
                pos_text = f"RICCHARD ({entity.position.x},{entity.position.y})"
                text_surface = font.render(pos_text, True, (0, 255, 0))
                self.screen.blit(text_surface, (cell_rect.x + 4, cell_rect.y + 4))
            elif getattr(entity, 'team', None) == 'player':
                pygame.draw.rect(self.screen, (0, 255, 255), cell_rect, 4)
                font = pygame.font.Font(None, 22)
                pos_text = f"{entity.name} ({entity.position.x},{entity.position.y})"
                text_surface = font.render(pos_text, True, (0, 255, 255))
                self.screen.blit(text_surface, (cell_rect.x + 4, cell_rect.y + 4))
            # Renderizar la entidad centrada en la celda lógica
            self._render_entity(entity, is_selected, is_marked_for_dash)
        if (game_context.current_state == GameState.TRACING_ROUTE and 
            game_context.current_route is not None):
            selected_entity = battle.get_entity(game_context.selected_entity_id)
            if selected_entity:
                self.movement_visualizer.render_route(
                    self.screen, 
                    game_context.current_route, 
                    selected_entity.position, 
                    is_dragging=False,
                    dash_anchors=getattr(game_context, 'dash_anchors', []),
                    camera_offset=self.camera_offset
                )
                # Marcadores visuales para depuración
                start_screen = self.movement_visualizer._position_to_screen(selected_entity.position, self.camera_offset)
                start_center = (start_screen[0] + self.movement_visualizer.cell_size // 2, start_screen[1] + self.movement_visualizer.cell_size // 2)
                pygame.draw.circle(self.screen, (0,0,255), start_center, 12)
                if game_context.current_route.path:
                    end_screen = self.movement_visualizer._position_to_screen(game_context.current_route.path[-1], self.camera_offset)
                    end_center = (end_screen[0] + self.movement_visualizer.cell_size // 2, end_screen[1] + self.movement_visualizer.cell_size // 2)
                    pygame.draw.circle(self.screen, (255,0,0), end_center, 12)
                    # Log visual y en consola del primer punto del path
                    first_screen = self.movement_visualizer._position_to_screen(game_context.current_route.path[0], self.camera_offset)
                    first_center = (first_screen[0] + self.movement_visualizer.cell_size // 2, first_screen[1] + self.movement_visualizer.cell_size // 2)
                    pygame.draw.circle(self.screen, (0,255,0), first_center, 12)
                    print(f"[ROUTE DEBUG] Personaje: {selected_entity.position} | Primer punto ruta: {game_context.current_route.path[0]}")
                # Log de posiciones en consola
                print(f"[ROUTE DEBUG] Posición inicial: {selected_entity.position}")
                print(f"[ROUTE DEBUG] Ruta completa: {[str(p) for p in game_context.current_route.path]}")
                # Dibujar todos los puntos de la ruta como círculos numerados
                font = pygame.font.Font(None, 18)
                for idx, pos in enumerate(game_context.current_route.path):
                    pt_screen = self.movement_visualizer._position_to_screen(pos, self.camera_offset)
                    pt_center = (pt_screen[0] + self.movement_visualizer.cell_size // 2, pt_screen[1] + self.movement_visualizer.cell_size // 2)
                    pygame.draw.circle(self.screen, (0,255,255), pt_center, 8)
                    text = font.render(str(idx), True, (0,0,0))
                    text_rect = text.get_rect(center=pt_center)
                    self.screen.blit(text, text_rect)
        if (game_context.current_state == GameState.ENTITY_SELECTED and 
            self.action_menu is not None):
            self.action_menu.draw(self.screen)
        self._render_state_info(game_context)
        self._render_ui(battle)
        self._render_visible_area_border()
        pygame.display.flip()
        self.clock.tick(60)

    def _render_entity(self, entity, is_selected: bool = False, is_marked_for_dash: bool = False):
        """Renderiza una entidad con marcado especial para embestidas"""
        pos = entity.position
        team = entity.team
        # Calcular la posición visual exacta de la celda lógica
        cell_rect = pygame.Rect(
            self.grid_offset[0] + pos.x * self.cell_size,
            self.grid_offset[1] + pos.y * self.cell_size,
            self.cell_size, self.cell_size
        )
        screen_x = cell_rect.x + self.cell_size // 2
        screen_y = cell_rect.y + self.cell_size // 2

        # Color según equipo
        if team == "player" or (hasattr(team, 'value') and team.value == "player"):
            color = (30, 144, 255)
        elif team == "enemy" or (hasattr(team, 'value') and team.value == "enemy"):
            color = self.colors["enemy"]
        else:
            color = self.colors["enemy"]

        # Dibujar entidad centrada en la celda lógica
        radius = self.cell_size // 3
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

        # Resaltar si está seleccionada
        if is_selected:
            pygame.draw.circle(self.screen, self.colors["selected"], 
                             (screen_x, screen_y), 
                             radius + 4, 3)  # Borde amarillo más grueso

        # Resaltar si está marcada para embestida
        if is_marked_for_dash:
            pygame.draw.circle(self.screen, (255, 50, 50),  # Rojo brillante
                             (screen_x, screen_y), 
                             radius + 8, 3)  # Círculo rojo exterior

        # Barra de salud
        health_percent = entity.stats.current_hp / entity.stats.max_hp
        bar_width = self.cell_size - 10
        bar_height = 8
        # Colocar la barra arriba de la entidad, pero dentro de la celda
        bar_x = cell_rect.x + (self.cell_size - bar_width) // 2
        bar_y = cell_rect.y + 4
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.colors["health_bar"], (bar_x, bar_y, int(bar_width * health_percent), bar_height))
        # Nombre de la entidad centrado arriba de la celda
        name_surface = self.font.render(entity.name, True, self.colors["text"])
        name_rect = name_surface.get_rect(center=(screen_x, bar_y - 16))
        self.screen.blit(name_surface, name_rect)

    def _render_obstacle(self, position: Position) -> None:
        """Renderiza un obstáculo centrado en la celda"""
        screen_x = self.grid_offset[0] + position.x * self.cell_size - self.camera_offset[0] + self.cell_size // 2
        screen_y = self.grid_offset[1] + position.y * self.cell_size - self.camera_offset[1] + self.cell_size // 2
        size = self.cell_size - 14
        rect = pygame.Rect(
            screen_x - size // 2,
            screen_y - size // 2,
            size,
            size
        )
        pygame.draw.rect(self.screen, self.colors["obstacle"], rect)

    def _render_state_info(self, game_context: GameContext):
        """Renderiza información del estado actual del juego adaptada a pantalla"""
        state_info = {
            GameState.IDLE: "💤 IDLE - Selecciona una entidad",
            GameState.ENTITY_SELECTED: "📋 ENTIDAD SELECCIONADA - Elige una acción",
            GameState.TRACING_ROUTE: "🛣️ TRAZANDO RUTA - Mueve el cursor, click en enemigos para embestida",
            GameState.TARGETING_ABILITY: "🎯 SELECCIONANDO OBJETIVO - Click en objetivo",
            GameState.AWAITING_CONFIRMATION: "⏳ CONFIRMACIÓN - Confirmando acción..."
        }
        state_text = state_info.get(game_context.current_state, "Estado desconocido")
        state_surface = self.font.render(state_text, True, (255, 255, 255))
        # Centrar el texto en la parte inferior de la pantalla
        state_rect = state_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(state_surface, state_rect)
        # Información adicional para modo trazado
        if (game_context.current_state == GameState.TRACING_ROUTE and 
            getattr(game_context, 'dash_anchors', [])):
            dash_info = f"Embestidas marcadas: {len(game_context.dash_anchors)}"
            dash_surface = self.font.render(dash_info, True, (255, 200, 200))
            dash_rect = dash_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 15))
            self.screen.blit(dash_surface, dash_rect)

    def _render_visible_area_border(self):
        """Dibuja un borde alrededor del área visible de la pantalla"""
        border_color = (255, 255, 0)
        border_thickness = 4
        pygame.draw.rect(
            self.screen,
            border_color,
            (0, 0, self.screen_width, self.screen_height),
            border_thickness
        )

    def move_camera(self, dx: int, dy: int):
        """Desplaza la cámara en píxeles, restringiendo al área del mapa"""
        max_offset_x = max(0, self.grid_offset[0] + self.grid_size[0] * self.cell_size - self.screen_width)
        max_offset_y = max(0, self.grid_offset[1] + self.grid_size[1] * self.cell_size - self.screen_height)
        self.camera_offset[0] = min(max(self.camera_offset[0] + dx, 0), max_offset_x)
        self.camera_offset[1] = min(max(self.camera_offset[1] + dy, 0), max_offset_y)

    def update_route_preview(self, route: Optional[MovementRoute]) -> None:
        """Actualiza la ruta que se está previsualizando"""
        self.current_route = route

    def set_action_menu(self, action_menu: Optional[ActionMenu]) -> None:
        """Establece el menú de acciones actual"""
        self.action_menu = action_menu

    def _render_ui(self, battle) -> None:
        """Renderiza la interfaz de usuario adaptada a pantalla y grid"""
        turn_color = self.colors["player_turn"] if battle.current_turn == "player" else self.colors["enemy_turn"]
        turn_text = f"TURNO: {'JUGADOR' if battle.current_turn == 'player' else 'ENEMIGO'}"
        turn_surface = self.big_font.render(turn_text, True, turn_color)
        turn_rect = turn_surface.get_rect(center=(self.screen_width // 2, self.grid_offset[1] // 2))
        self.screen.blit(turn_surface, turn_rect)
        info_lines = [
            f"Acciones: {battle.actions_remaining}/3",
            f"Turno: {battle.turn_count}",
            f"Modo: {battle.mode}",
            f"Jugadores: {len(battle.get_player_entities())} | Enemigos: {len(battle.get_enemy_entities())}"
        ]
        for i, line in enumerate(info_lines):
            info_surface = self.font.render(line, True, self.colors["text"])
            info_rect = info_surface.get_rect(topleft=(self.grid_offset[0], self.grid_offset[1] - 40 + i * 25))
            self.screen.blit(info_surface, info_rect)
        controls = [
            "CONTROLES:",
            "CLICK - Seleccionar/Mover entidad", 
            "ESPACIO - Terminar turno",
            "R - Reiniciar batalla",
            "ESC - Salir"
        ]
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, self.colors["text"])
            control_rect = control_surface.get_rect(topright=(self.screen_width - self.grid_offset[0], self.grid_offset[1] - 40 + i * 25))
            self.screen.blit(control_surface, control_rect)

    def _render_grid(self) -> None:
        """Renderiza el grid táctico adaptado a pantalla"""
        font = pygame.font.Font(None, 18)
        # Dibujar líneas del grid
        for x in range(self.grid_size[0] + 1):
            start_x = self.grid_offset[0] + x * self.cell_size - self.camera_offset[0]
            pygame.draw.line(
                self.screen, self.colors["grid"],
                (start_x, self.grid_offset[1] - self.camera_offset[1]),
                (start_x, self.grid_offset[1] + self.grid_size[1] * self.cell_size - self.camera_offset[1])
            )
        for y in range(self.grid_size[1] + 1):
            start_y = self.grid_offset[1] + y * self.cell_size - self.camera_offset[1]
            pygame.draw.line(
                self.screen, self.colors["grid"],
                (self.grid_offset[0] - self.camera_offset[0], start_y),
                (self.grid_offset[0] + self.grid_size[0] * self.cell_size - self.camera_offset[0], start_y)
            )
        # Dibujar coordenadas en cada celda
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                rect = pygame.Rect(
                    self.grid_offset[0] + x * self.cell_size - self.camera_offset[0],
                    self.grid_offset[1] + y * self.cell_size - self.camera_offset[1],
                    self.cell_size, self.cell_size
                )
                coord_text = f"({x},{y})"
                text_surface = font.render(coord_text, True, (180, 180, 180))
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

    def _render_valid_moves(self, valid_moves: List[Position]) -> None:
        """Renderiza las posiciones de movimiento válidas adaptadas al grid"""
        if not valid_moves:
            return
        for pos in valid_moves:
            screen_x = self.grid_offset[0] + pos.x * self.cell_size - self.camera_offset[0] + 5
            screen_y = self.grid_offset[1] + pos.y * self.cell_size - self.camera_offset[1] + 5
            highlight = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
            highlight.fill(self.colors["valid_move"])
            self.screen.blit(highlight, (screen_x, screen_y))