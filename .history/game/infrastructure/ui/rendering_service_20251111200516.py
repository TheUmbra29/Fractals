"""
SERVICIO DE RENDERIZADO - Con imports ABSOLUTOS
"""
import pygame
from typing import List, Optional
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.game_enums import Team

class RenderingService:
    def to_screen_coords(self, tile_x, tile_y):
        """Convierte coordenadas de grid a coordenadas de pantalla centradas en la celda"""
        return (
            int(self.grid_offset[0] + tile_x * self.cell_size + self.cell_size // 2),
            int(self.grid_offset[1] + tile_y * self.cell_size + self.cell_size // 2)
        )
    """Servicio de renderizado especializado"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = None
        self.big_font = None
        
        self.colors = {
            "background": (25, 25, 40),
            "grid": (60, 60, 80),
            "grid_highlight": (100, 100, 150),
            "player": (65, 105, 225),
            "enemy": (220, 20, 60),
            "obstacle": (100, 100, 100),
            "text": (255, 255, 255),
            "ui_background": (40, 40, 60, 200),
            "health_bar": (50, 200, 50),
            "ph_bar": (30, 144, 255),
            "selected": (255, 255, 0),
            "valid_move": (100, 200, 100, 100),
            "player_turn": (100, 255, 100),
            "enemy_turn": (255, 100, 100),
        }
        
        self.grid_size = (8, 8)
        self.cell_size = 60
        self.grid_offset = (100, 100)
    
    def initialize(self) -> None:
        """Inicializa Pygame y recursos gráficos y ajusta grid_size, cell_size y offset"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("FRACTALS - Arquitectura Limpia")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 32)
        # Ajustar grid_size al laboratorio
        self.grid_size = (16, 12)
        # Calcular cell_size y offset para que el grid ocupe toda la pantalla
        self.cell_size = min(
            (self.screen_width - 40) // self.grid_size[0],
            (self.screen_height - 40) // self.grid_size[1]
        )
        self.grid_offset = (
            (self.screen_width - self.cell_size * self.grid_size[0]) // 2,
            (self.screen_height - self.cell_size * self.grid_size[1]) // 2
        )
        print("🎨 Renderizador inicializado")
    
    def render_battle(self, battle, selected_entity_id: Optional[str] = None, valid_moves: List[Position] = None) -> None:
        """Renderiza el estado completo de la batalla"""
        self.screen.fill(self.colors["background"])

        # Renderizar elementos en orden
        self._render_grid()
        self._render_valid_moves(valid_moves)

        for obstacle in battle._obstacles:
            self._render_obstacle(obstacle)

        for entity in battle._entities.values():
            is_selected = entity.id == selected_entity_id
            self._render_entity(entity, is_selected)

        self._render_ui(battle)

        pygame.display.flip()
        self.clock.tick(60)
    
    def _render_grid(self) -> None:
        """Renderiza el grid táctico"""
        for x in range(self.grid_size[0] + 1):
            start = self.to_screen_coords(x, 0)
            end = self.to_screen_coords(x, self.grid_size[1])
            pygame.draw.line(
                self.screen, self.colors["grid"],
                start,
                end
            )
        for y in range(self.grid_size[1] + 1):
            start = self.to_screen_coords(0, y)
            end = self.to_screen_coords(self.grid_size[0], y)
            pygame.draw.line(
                self.screen, self.colors["grid"],
                start,
                end
            )
    
    def _render_valid_moves(self, valid_moves: List[Position]) -> None:
        """Renderiza las posiciones de movimiento válidas"""
        if not valid_moves:
            return
            
        for pos in valid_moves:
            screen_x = self.grid_offset[0] + pos.x * self.cell_size
            screen_y = self.grid_offset[1] + pos.y * self.cell_size
            
            # Crear superficie semitransparente
            highlight = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
            highlight.fill(self.colors["valid_move"])
            self.screen.blit(highlight, (screen_x + 5, screen_y + 5))
    
    def _render_entity(self, entity, is_selected: bool = False) -> None:
        """Renderiza una entidad en el grid"""
        pos = entity.position
        team = entity.team

        print(f"🔍 RENDER_ENTITY DEBUG:")
        print(f"   - Nombre: {entity.name}")
        print(f"   - Team: {team} (tipo: {type(team)})")
        print(f"   - Team value: {team.value if hasattr(team, 'value') else 'N/A'}")
        print(f"   - Team == Team.PLAYER: {team == Team.PLAYER}")
        print(f"   - Team == 'player': {team == 'player'}")
        print(f"   - Team == Team.ENEMY: {team == Team.ENEMY}")
        print(f"   - Team == 'enemy': {team == 'enemy'}")

        screen_x = self.grid_offset[0] + pos.x * self.cell_size
        screen_y = self.grid_offset[1] + pos.y * self.cell_size

        color = None
        if team == Team.PLAYER:
            color = self.colors["player"]
            print(f"   - COLOR: AZUL (Player)")
        elif team == Team.ENEMY:
            color = self.colors["enemy"] 
            print(f"   - COLOR: ROJO (Enemy)")
        else:
            # Fallback por si acaso
            color = self.colors["enemy"]
            print(f"   - COLOR: ROJO (Fallback - team desconocido: {team})")

        if team == Team.PLAYER or (isinstance(team, str) and team.upper() == "PLAYER"):
            color = self.colors["player"]
        else:
            color = self.colors["enemy"]

        # Dibujar entidad
        radius = self.cell_size // 3
        pygame.draw.circle(self.screen, color, (screen_x + self.cell_size//2, screen_y + self.cell_size//2), radius)

        # Resaltar si está seleccionada
        if is_selected:
            pygame.draw.circle(self.screen, self.colors["selected"],
                             (screen_x + self.cell_size//2, screen_y + self.cell_size//2),
                             radius + 2, 2)  # Borde amarillo

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
    
    def _render_obstacle(self, position: Position) -> None:
        """Renderiza un obstáculo"""
        screen_x = self.grid_offset[0] + position.x * self.cell_size
        screen_y = self.grid_offset[1] + position.y * self.cell_size
        
        pygame.draw.rect(
            self.screen, self.colors["obstacle"],
            (screen_x + 5, screen_y + 5, self.cell_size - 10, self.cell_size - 10)
        )
    
    def _render_ui(self, battle) -> None:
        """Renderiza la interfaz de usuario actualizada con enums"""

        turn_color = self.colors["player_turn"] if battle.current_turn == Team.PLAYER else self.colors["enemy_turn"]
        turn_text = f"TURNO: {'JUGADOR' if battle.current_turn == Team.PLAYER else 'ENEMIGO'}"
        turn_surface = self.big_font.render(turn_text, True, turn_color)
        self.screen.blit(turn_surface, (20, 20))

        info_lines = [
            f"Acciones: {battle.actions_remaining}/3",
            f"Turno: {battle.turn_count}",
            f"Modo: {battle.mode}",
            f"Jugadores: {len(battle.get_player_entities())} | Enemigos: {len(battle.get_enemy_entities())}"
        ]
        for i, line in enumerate(info_lines):
            info_surface = self.font.render(line, True, self.colors["text"])
            self.screen.blit(info_surface, (20, 60 + i * 25))
        controls = [
            "CONTROLES:",
            "CLICK - Seleccionar/Mover entidad", 
            "ESPACIO - Terminar turno",
            "R - Reiniciar batalla",
            "ESC - Salir"
        ]
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, self.colors["text"])
            self.screen.blit(control_surface, (500, 20 + i * 25))
    
    def cleanup(self) -> None:
        """Limpia recursos de Pygame"""
        try:
            pygame.quit()
        except:
            pass