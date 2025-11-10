"""
GAME LOOP ACTUALIZADO - Con sistema de rutas y arrastre
"""
import pygame
from uuid import uuid4

from core.domain.entities.aggregates.battle import Battle
from core.domain.entities.battle_entity import BattleEntity
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.stats import EntityStats

from .input_service import InputService
from .enhanced_rendering_service import EnhancedRenderingService

class GameLoop:
    """Coordina el flujo del juego con sistema de rutas dinámicas"""
    
    def __init__(self, battle_repository, turn_service):
        self.battle_repo = battle_repository
        self.turn_service = turn_service
        self.input_service = InputService()
        self.renderer = EnhancedRenderingService()
        
        self.current_battle_id = None
        self.selected_entity_id = None
        self.running = False
        self.valid_moves = []
        
        # ESTADOS NUEVOS PARA EL SISTEMA DE RUTAS
        self.is_dragging = False
        self.drag_start_pos = None
        self.current_route = None
    
    def run(self):
        """Bucle principal con sistema de arrastre"""
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
        print("🎯 Controles: Click y ARRASTRA para ver rutas, SOLTAR para mover")
        print("🎯 ESPACIO para terminar turno, R para reiniciar")
    
    def _process_input(self):
        """Procesa entrada con soporte para drag & drop"""
        self.input_service.process_events()
        
        # Comandos de salida
        if self.input_service.is_key_pressed("QUIT") or self.input_service.is_key_pressed("ESCAPE"):
            self.running = False
        
        # Comandos de juego
        if self.input_service.is_key_pressed("SPACE"):
            self._handle_end_turn_command()
        
        if self.input_service.is_key_pressed("RESET"):
            self._handle_reset_command()
        
        # SISTEMA DE ARRASTRE - NUEVO
        self._handle_drag_system()
    
    def _handle_drag_system(self):
        """Maneja todo el sistema de arrastre para movimiento"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        
        # Obtener estado actual del mouse
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Click inicial - seleccionar entidad
        if self.input_service.is_mouse_clicked() and not self.is_dragging:
            self._handle_mouse_click_start(battle)
        
        # ✅ CAMBIO IMPORTANTE: Usar estado directo del mouse en lugar de eventos
        if mouse_buttons[0] and self.selected_entity_id:  # Botón izquierdo presionado
            if not self.is_dragging:
                self.is_dragging = True
                print("🖱️  Iniciando arrastre...")
            self._handle_drag_update(battle)
        elif self.is_dragging and not mouse_buttons[0]:  # Botón liberado
            self._handle_drag_end(battle)
    
    def _handle_mouse_click_start(self, battle):
        """Maneja el inicio del click para seleccionar entidad"""
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
            # Seleccionar entidad del jugador e iniciar arrastre
            self.selected_entity_id = clicked_entity.id
            self.valid_moves = self.turn_service.get_valid_moves(self.current_battle_id, self.selected_entity_id)
            self.is_dragging = True
            self.drag_start_pos = clicked_entity.position
            print(f"🎯 Seleccionado: {clicked_entity.name}")
            print("🖱️  Arrastra para ver la ruta y embestidas")
    
    def _handle_drag_update(self, battle):
        """Actualiza la ruta en tiempo real durante el arrastre"""
        grid_pos = self.input_service.get_mouse_grid_position(
            self.renderer.grid_offset,
            self.renderer.cell_size, 
            self.renderer.grid_size
        )
        
        if not grid_pos:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
            return
            
        target_pos = Position(grid_pos[0], grid_pos[1])
        selected_entity = battle.get_entity(self.selected_entity_id)
        
        # ✅ EVITAR CALCULAR RUTA SI ES LA MISMA POSICIÓN
        if selected_entity and selected_entity.position == target_pos:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
            return
        
        if selected_entity:
            try:
                # Calcular ruta en tiempo real con detección de embestidas
                self.current_route = self.turn_service.calculate_movement_route(
                    self.current_battle_id, self.selected_entity_id, target_pos
                )
                self.renderer.update_route_preview(self.current_route, True)
                
                # Debug info
                if self.current_route:
                    print(f"🛣️  Ruta calculada: {len(self.current_route.path)} pasos, Válida: {self.current_route.is_valid}")
                    if self.current_route.dash_targets:
                        print(f"⚔️  Embestidas detectadas: {len(self.current_route.dash_targets)} enemigos")
                else:
                    print("❌ No se pudo calcular ruta")
                    
            except Exception as e:
                print(f"❌ Error calculando ruta: {e}")
                self.current_route = None
                self.renderer.update_route_preview(None, False)
        else:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
    
    def _handle_drag_end(self, battle):
        """Ejecuta el movimiento cuando se suelta el mouse"""
        if not self.selected_entity_id:
            self.is_dragging = False
            return
            
        grid_pos = self.input_service.get_mouse_grid_position(
            self.renderer.grid_offset,
            self.renderer.cell_size,
            self.renderer.grid_size
        )
        
        if grid_pos:
            target_pos = Position(grid_pos[0], grid_pos[1])
            
            try:
                # Ejecutar movimiento con embestidas automáticas
                message = self.turn_service.execute_movement_with_dashes(
                    self.current_battle_id, self.selected_entity_id, target_pos
                )
                print(f"➡️  {message}")
                
            except Exception as e:
                print(f"❌ Error al mover: {e}")
        
        # Resetear estado de arrastre
        self._reset_drag_state()
    
    def _reset_drag_state(self):
        """Resetea todo el estado del sistema de arrastre"""
        self.is_dragging = False
        self.drag_start_pos = None
        self.current_route = None
        self.renderer.update_route_preview(None, False)
    
    def _update_game_state(self):
        """Actualiza estado del juego"""
        # Por ahora vacío, la lógica está en los servicios
        pass
    
    def _render_frame(self):
        """Renderiza el frame con rutas dinámicas"""
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
        print(f"✔️ Batalla creada: {player.name} vs {enemy.name}")
        return battle_id
    
    def _get_entity_at_position(self, battle, position):
        """Busca entidad en posición"""
        for entity in battle._entities.values():
            if entity.position == position:
                return entity
        return None

    def _handle_end_turn_command(self):
        """Termina el turno y limpia estado"""
        try:
            events = self.turn_service.end_player_turn(self.current_battle_id)
            print("🔚 Turno terminado")
            for event in events:
                print(f"📢 {type(event).__name__}")
            
            # Limpiar estado
            self.selected_entity_id = None
            self.valid_moves = []
            self._reset_drag_state()
            
        except Exception as e:
            print(f"❌ Error al terminar turno: {e}")
    
    def _handle_reset_command(self):
        """Reinicia la batalla"""
        self.current_battle_id = self._create_initial_battle()
        self.selected_entity_id = None
        self.valid_moves = []
        self._reset_drag_state()
        print("🔄 Batalla reiniciada")

    def _handle_drag_update(self, battle):
        """Actualiza la ruta en tiempo real durante el arrastre"""
        grid_pos = self.input_service.get_mouse_grid_position(
            self.renderer.grid_offset,
            self.renderer.cell_size, 
            self.renderer.grid_size
        )
        
        if not grid_pos:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
            return
            
        target_pos = Position(grid_pos[0], grid_pos[1])
        selected_entity = battle.get_entity(self.selected_entity_id)
        
        if not selected_entity:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
            return
        
        # Evitar calcular ruta si es la misma posición
        if selected_entity.position == target_pos:
            self.current_route = None
            self.renderer.update_route_preview(None, False)
            return
        
        try:
            # Calcular ruta en tiempo real con detección de embestidas
            self.current_route = self.turn_service.calculate_movement_route(
                self.current_battle_id, self.selected_entity_id, target_pos
            )
            self.renderer.update_route_preview(self.current_route, True)
                
        except Exception as e:
            # Solo mostrar errores reales, no los de "misma posición"
            if "misma posición" not in str(e):
                print(f"❌ Error calculando ruta: {e}")
            self.current_route = None
            self.renderer.update_route_preview(None, False)