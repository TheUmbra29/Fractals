"""
GAME LOOP - Con imports ABSOLUTOS
"""
import pygame
from uuid import uuid4

from core.domain.entities.aggregates.battle import Battle
from core.domain.entities.battle_entity import BattleEntity
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.stats import EntityStats

from .input_service import InputService
from .rendering_service import RenderingService

class GameLoop:
    """Coordina el flujo del juego - Sin lógica de negocio"""
    
    def __init__(self, battle_repository, turn_service):
        self.battle_repo = battle_repository
        self.turn_service = turn_service
        self.input_service = InputService()
        self.renderer = RenderingService()
        
        self.current_battle_id = None
        self.selected_entity_id = None
        self.running = False
        self.valid_moves = []
    
    def run(self):
        """Bucle principal - Solo coordina, no implementa"""
        try:
            self._initialize()
            
            while self.running:
                self._process_input()
                self._update_game_state() 
                self._render_frame()
                
        except Exception as e:
            print(f"💥 Error en game loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.renderer.cleanup()
    
    def _initialize(self):
        """Inicializa todos los sistemas"""
        self.renderer.initialize()
        self.current_battle_id = self._create_initial_battle()
        self.running = True
        print("🎮 Game Loop inicializado")
        print("🎯 Controles: Click para seleccionar/mover, ESPACIO para terminar turno")
    
    def _process_input(self):
        """Procesa entrada - Delega al InputService"""
        self.input_service.process_events()
        
        # Comandos de salida
        if self.input_service.is_key_pressed("QUIT") or self.input_service.is_key_pressed("ESCAPE"):
            self.running = False
        
        # Comandos de juego
        if self.input_service.is_key_pressed("SPACE"):
            self._handle_end_turn_command()
        
        if self.input_service.is_key_pressed("RESET"):
            self._handle_reset_command()
        
        if self.input_service.is_mouse_clicked():
            self._handle_mouse_click_command()
    
    def _handle_end_turn_command(self):
        """Delega el fin de turno al servicio especializado"""
        try:
            events = self.turn_service.end_player_turn(self.current_battle_id)
            print("🔚 Turno terminado")
            for event in events:
                print(f"📢 {type(event).__name__}")
            self.selected_entity_id = None
            self.valid_moves = []
        except Exception as e:
            print(f"❌ Error al terminar turno: {e}")
    
    def _handle_reset_command(self):
        """Reinicia la batalla"""
        self.current_battle_id = self._create_initial_battle()
        self.selected_entity_id = None
        self.valid_moves = []
        print("🔄 Batalla reiniciada")
    
    def _handle_mouse_click_command(self):
        """Delega el manejo de clicks"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        grid_pos = self.input_service.get_mouse_grid_position(
            self.renderer.grid_offset, 
            self.renderer.cell_size, 
            self.renderer.grid_size
        )
        
        if not grid_pos:
            return
            
        target_pos = Position(grid_pos[0], grid_pos[1])
        
        # Buscar entidad clickeada
        clicked_entity = self._get_entity_at_position(battle, target_pos)
        
        if clicked_entity and clicked_entity.team == "player":
            # Seleccionar entidad del jugador
            self.selected_entity_id = clicked_entity.id
            self.valid_moves = self.turn_service.get_valid_moves(self.current_battle_id, self.selected_entity_id)
            print(f"🎯 Seleccionado: {clicked_entity.name}")
            print(f"📍 Movimientos válidos: {len(self.valid_moves)}")
        
        elif self.selected_entity_id and battle.current_turn == "player":
            # Mover entidad seleccionada
            try:
                message = self.turn_service.move_entity(
                    self.current_battle_id, self.selected_entity_id, target_pos
                )
                print(f"➡️ {message}")
                self.valid_moves = []
            except Exception as e:
                print(f"❌ {e}")
    
    def _update_game_state(self):
        """Actualiza estado del juego - Podría incluir IA en el futuro"""
        # Por ahora vacío, la lógica está en los servicios
        pass
    
    def _render_frame(self):
        """Delega el renderizado al servicio especializado"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        self.renderer.render_battle(battle, self.selected_entity_id, self.valid_moves)
    
    def _create_initial_battle(self):
        """Crea batalla inicial"""
        battle_id = uuid4()
        battle = Battle(battle_id, mode="arcade", grid_size=(8, 8))
        
        # Crear jugador
        player = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(1, 1),
            stats=EntityStats(100, 100, 50, 50, 25, 15, 10),
            team="player",
            name="Ricchard",
            character_class="Daño"
        )
        
        # Crear enemigo
        enemy = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(6, 6),
            stats=EntityStats(80, 80, 30, 30, 20, 10, 8),
            team="enemy", 
            name="Enemy Bot",
            character_class="Daño"
        )
        
        # Añadir obstáculos
        battle.add_obstacle(Position(3, 3))
        battle.add_obstacle(Position(4, 4))
        battle.add_obstacle(Position(2, 5))
        
        battle.add_entity(player)
        battle.add_entity(enemy)
        
        self.battle_repo.save(battle)
        print(f"⚔️ Batalla creada: {player.name} vs {enemy.name}")
        return battle_id
    
    def _get_entity_at_position(self, battle, position):
        """Busca entidad en posición - Helper method"""
        for entity in battle._entities.values():
            if entity.position == position:
                return entity
        return None