"""
GAME LOOP ACTUALIZADO - Sistema de embestidas como puntos de anclaje
"""
import pygame
from uuid import uuid4

from core.domain.entities.aggregates.battle import Battle
from core.domain.entities.battle_entity import BattleEntity
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.stats import EntityStats
from core.domain.entities.value_objects.game_enums import Team, CharacterClass

from .input_service import InputService
from .enhanced_rendering_service import EnhancedRenderingService
from .game_states import GameState, GameContext
from .action_menu import ActionMenu
from core.presentation.ability_menu import AbilityMenu
from typing import List

class GameLoop:
    def handle_attack(self, attacker_id: str, target_id: str):
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        attacker = battle.get_entity(attacker_id)
        defender = battle.get_entity(target_id)
        # Calcular ataque con cobertura
        result = battle.calculate_attack(attacker, defender)
        # Actualizar estados de cobertura para todas las entidades
        for entity in battle.get_entities():
            enemies = [e for e in battle.get_entities() if e.team != entity.team]
            if hasattr(entity, 'update_cover_status'):
                entity.update_cover_status(battle.cover_system, enemies)
        return result
    def _handle_input_targeting_ability(self):
        """Procesa el uso de habilidades tipo Habilidad"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        selected_entity = battle.get_entity(self.context.selected_entity_id)
        if not selected_entity:
            self._clear_selection()
            return
        if self.input_service.is_mouse_clicked():
            grid_pos = self.input_service.get_mouse_grid_position(
                self.renderer.grid_offset,
                self.renderer.cell_size,
                self.renderer.grid_size
            )
            if not grid_pos:
                return
            target_pos = Position(grid_pos[0], grid_pos[1])
            objetivo = self._get_entity_at_position(battle, target_pos)
            habilidad_id = self.context.pending_action
            resultado = selected_entity.usar_habilidad(habilidad_id, objetivo, battle)
            print(resultado)
            self._clear_selection()
    """Coordina el flujo del juego con sistema de anclajes para embestidas"""
    
    def __init__(self, battle_repository, turn_service):
        self.battle_repo = battle_repository
        self.turn_service = turn_service
        self.input_service = InputService()
        self.renderer = EnhancedRenderingService()
        self.current_battle_id = None
        self.running = False
        self.context = GameContext()
        self.action_menu = None
        self.ability_menu = None  # Nuevo menú de habilidades
        self.valid_moves = []
        self.last_cursor_pos = None  # Última posición del cursor para trazado
        
        print("🎮 Game Loop inicializado - Sistema de anclajes activo")
    
    def run(self):
        """Bucle principal con gestión de estados"""
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
        """Inicializa el juego en estado IDLE"""
        self.renderer.initialize()
        self.current_battle_id = self._create_initial_battle()
        self.running = True
        self.context.reset()
        print("🚀 Juego inicializado - Selecciona una entidad para comenzar")
        print("🎯 Nuevo sistema: Click en enemigos durante trazado para añadir puntos de embestida")
    
    def _process_input(self):
        """Procesa input según el estado actual"""
        self.input_service.process_events()
        
        # Comandos globales (siempre disponibles)
        if self.input_service.is_key_pressed("QUIT") or self.input_service.is_key_pressed("ESCAPE"):
            self.running = False
        
        if self.input_service.is_key_pressed("RESET"):
            self._handle_reset_command()
        
        if self.input_service.is_key_pressed("SPACE"):
            self._handle_end_turn_command()
        
        # Manejo de input por estado
        state_handlers = {
            GameState.IDLE: self._handle_input_idle,
            GameState.ENTITY_SELECTED: self._handle_input_entity_selected,
            GameState.TRACING_ROUTE: self._handle_input_tracing_route,
            GameState.TARGETING_ABILITY: self._handle_input_targeting_ability,
        }
        
        handler = state_handlers.get(self.context.current_state)
        if handler:
            handler()
    
    def _handle_input_idle(self):
        """Estado IDLE: Click en entidades del jugador para seleccionar"""
        if self.input_service.is_mouse_clicked():
            battle = self.battle_repo.get_by_id(self.current_battle_id)
            grid_pos = self.input_service.get_mouse_grid_position(
                self.renderer.grid_offset, 
                self.renderer.cell_size, 
                self.renderer.grid_size
            )
            
            if not grid_pos:
                return
                
            target_pos = Position(grid_pos[0], grid_pos[1])
            cursor_pos = target_pos  # Definir cursor_pos correctamente
            clicked_entity = self._get_entity_at_position(battle, target_pos)

            # Validar que sea entidad del jugador y sea su turno
            if (clicked_entity and 
                clicked_entity.team == Team.PLAYER and 
                battle.current_turn == Team.PLAYER):
                self.last_cursor_pos = cursor_pos  # Actualizar última posición del cursor

                self.context.selected_entity_id = clicked_entity.id
                self.context.current_state = GameState.ENTITY_SELECTED

                # Mostrar menú de acciones
                screen_pos = self._position_to_screen(clicked_entity.position)
                self.action_menu = ActionMenu(clicked_entity, screen_pos)

                print(f"🎯 {clicked_entity.name} seleccionado")
                print("📋 Menú de acciones disponible - Elige una acción")
    
    def _handle_input_entity_selected(self):
        """Estado ENTITY_SELECTED: Interactuar con menú de acciones"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        selected_entity = battle.get_entity(self.context.selected_entity_id)
        
        if not selected_entity:
            self._clear_selection()
            return
        
        # El menú de habilidades se abre solo al seleccionar 'Atacar' en el menú de acciones
        
        # Click en el menú de acciones
        if self.input_service.is_mouse_clicked():
            mouse_pos = self.input_service.get_mouse_position()
            selected_action = self.action_menu.handle_click(mouse_pos)
            if selected_action == "attack_menu":
                screen_pos = self._position_to_screen(selected_entity.position)
                self.ability_menu = AbilityMenu(selected_entity, screen_pos)
                self.renderer.ability_menu = self.ability_menu  # Asignar al renderer
                self.context.current_state = GameState.ABILITY_MENU
                print("🧙 Menú de habilidades abierto")
            elif selected_action:
                self._handle_action_selection(selected_action, selected_entity)
            else:
                # Click fuera del menú - deseleccionar
                self._clear_selection()
        
        # Si el menú de habilidades está visible, procesar input
        if self.ability_menu and self.ability_menu.visible and self.context.current_state == GameState.ABILITY_MENU:
            for event in pygame.event.get():
                habilidad_id = self.ability_menu.handle_input(event)
                if habilidad_id:
                    self._handle_action_selection(habilidad_id, selected_entity)
                    self.ability_menu.visible = False
                    self.context.current_state = GameState.ENTITY_SELECTED  # Vuelve al estado anterior
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.ability_menu.visible = False
                    self.context.current_state = GameState.ENTITY_SELECTED  # Vuelve al estado anterior
    
    def _handle_input_tracing_route(self):
        """Estado TRACING_ROUTE: Trazado de ruta con sistema de anclajes"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        selected_entity = battle.get_entity(self.context.selected_entity_id)
        
        if not selected_entity:
            self._clear_selection()
            return
        
        # Obtener posición actual del cursor en el grid
        grid_pos = self.input_service.get_mouse_grid_position(
            self.renderer.grid_offset,
            self.renderer.cell_size, 
            self.renderer.grid_size
        )
        
        if grid_pos:
            cursor_pos = Position(grid_pos[0], grid_pos[1])
            self.last_cursor_pos = cursor_pos  # Actualizar última posición del cursor
            
            # ACTUALIZAR RUTA EN TIEMPO REAL con anclajes actuales
            self._update_route_preview(selected_entity, cursor_pos, battle)
            
            # Click: marcar anclaje de embestida o confirmar movimiento
            if self.input_service.is_mouse_clicked():
                self._handle_route_click(battle, cursor_pos, selected_entity)
    
    def _handle_action_selection(self, action_type: str, entity):
        """Procesa selección de acción del menú"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        if action_type == "move":
            self.context.current_state = GameState.TRACING_ROUTE
            self.context.pending_action = "move"
            self.action_menu.set_visibility(False)
            self.valid_moves = []
            print("🛣️ Modo TRAZADO DE RUTA activado")
            print("💡 Mueve el cursor para ver la ruta")
            print("🎯 Click en enemigos para añadir puntos de embestida")
            print("💡 Click en casilla vacía para confirmar movimiento")
        elif any(hab.id == action_type for hab in entity.habilidades):
            self.context.current_state = GameState.TARGETING_ABILITY
            self.context.pending_action = action_type
            self.action_menu.set_visibility(False)
            print(f"🔮 Modo {action_type.upper()} - Selecciona objetivo")
    
    def _update_route_preview(self, entity: BattleEntity, destination: Position, battle: Battle):
        """Actualiza la previsualización de ruta con anclajes actuales"""
        
        try:
            # Calcular ruta que pasa por todos los anclajes
            route = self.turn_service.calculate_route_with_anchors(
                self.current_battle_id,
                self.context.selected_entity_id,
                destination,
                self.context.dash_anchors
            )
            # Si la ruta está vacía pero el destino es válido, mostrar al menos el punto actual
            if not route or not route.path:
                route = type(route)([entity.position], [], True)
            self.context.current_route = route
            self.renderer.update_route_preview(self.context.current_route)
        except Exception as e:
            print(f"❌ Error calculando ruta: {e}")
            self.context.current_route = None
            self.renderer.update_route_preview(None)
    
    def _handle_route_click(self, battle, click_pos: Position, selected_entity: BattleEntity):
        """Maneja clicks durante el trazado de ruta - SISTEMA DE ANCLAJES"""
        clicked_entity = self._get_entity_at_position(battle, click_pos)
        
        if clicked_entity and clicked_entity.team == Team.ENEMY:
            # MARCAR/DESMARCAR punto de anclaje para embestida
            enemy_pos = clicked_entity.position
            ruta_actualizada = False
            if enemy_pos in self.context.dash_anchors:
                # Desmarcar anclaje
                self.context.dash_anchors.remove(enemy_pos)
                print(f"❌ Embestida desmarcada: {clicked_entity.name}")
                ruta_actualizada = True
            else:
                # Marcar anclaje - verificar que no sea el mismo enemigo
                anchored_enemies = self._get_anchored_enemies(battle)
                if clicked_entity.id not in [e.id for e in anchored_enemies]:
                    self.context.dash_anchors.append(enemy_pos)
                    print(f"🎯 Embestida marcada: {clicked_entity.name} (Anclaje #{len(self.context.dash_anchors)})")
                    # Mostrar información de anclajes actuales
                    if len(self.context.dash_anchors) > 0:
                        print(f"📌 Anclajes activos: {len(self.context.dash_anchors)}")
                    ruta_actualizada = True
                else:
                    print(f"⚠️ Ya has marcado a {clicked_entity.name} para embestida")
            # Forzar actualización de la ruta para evitar que desaparezca
            if ruta_actualizada:
                self._update_route_preview(selected_entity, click_pos, battle)
            
        else:
            # CONFIRMAR movimiento final con anclajes
            try:
                message = self.turn_service.execute_movement_with_dash_anchors(
                    self.current_battle_id, 
                    self.context.selected_entity_id,
                    click_pos,
                    self.context.dash_anchors
                )
                print(f"➡️ {message}")
                self._clear_selection()
                
            except Exception as e:
                print(f"❌ Error en movimiento: {e}")
    
    def _get_anchored_enemies(self, battle) -> List[BattleEntity]:
        """Obtiene las entidades enemigas en las posiciones de anclaje"""
        anchored_enemies = []
        for anchor_pos in self.context.dash_anchors:
            enemy = battle.get_entity_at_position(anchor_pos)
            if enemy:
                anchored_enemies.append(enemy)
        return anchored_enemies
    
    def _clear_selection(self):
        """Limpia toda la selección y vuelve al estado IDLE"""
        self.context.reset()
        self.action_menu = None
        self.ability_menu = None
        self.valid_moves = []
        print("🧹 Selección limpiada")
    
    def _update_game_state(self):
        """Actualiza estado del juego"""
        # Por ahora vacío, la lógica está en los servicios
        pass
    
    def _render_frame(self):
        """Renderiza el frame con rutas y anclajes"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        
        # Pasar el contexto al renderizador
        self.renderer.set_action_menu(self.action_menu)
        self.renderer.render_battle(battle, self.context, self.valid_moves)
        # Renderizar menú de habilidades si está activo
        if self.ability_menu and self.ability_menu.visible:
            self.ability_menu.draw(self.renderer.screen)
    
    def _create_initial_battle(self):
        """Crea batalla inicial usando enums"""
        battle_id = uuid4()
        battle = Battle(battle_id, mode="arcade", grid_size=(8, 8))
        
        # Crear jugador
        player = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(1, 1),
            stats=EntityStats(100, 100, 50, 50, 25, 15, 10),
            team=Team.PLAYER,
            name="Ricchard",
            character_class=CharacterClass.DAMAGE
        )
        
        # Crear enemigos
        enemy1 = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(6, 6),
            stats=EntityStats(80, 80, 30, 30, 20, 10, 8),
            team=Team.ENEMY,
            name="Enemy Bot 1",
            character_class=CharacterClass.DAMAGE
        )
        
        enemy2 = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(4, 4),
            stats=EntityStats(70, 70, 25, 25, 18, 8, 6),
            team=Team.ENEMY,
            name="Enemy Bot 2",
            character_class=CharacterClass.DAMAGE
        )
        
        # Añadir obstáculos desde configuración
        from core.domain.config.game_config import GAME_CONFIG
        for obstacle_pos in GAME_CONFIG.INITIAL_OBSTACLES:
            battle.add_obstacle(Position(obstacle_pos[0], obstacle_pos[1]))
        
        battle.add_entity(player)
        battle.add_entity(enemy1)
        battle.add_entity(enemy2)
        
        self.battle_repo.save(battle)
        print(f"✔️ Batalla creada: {player.name} vs {enemy1.name} y {enemy2.name}")
        return battle_id
    
    def _get_entity_at_position(self, battle, position):
        """Busca entidad en posición"""
        for entity in battle.get_entities():
            if entity.position == position:
                return entity
        return None
    
    def _position_to_screen(self, position: Position) -> tuple:
        """Convierte posición del grid a coordenadas de pantalla"""
        x = self.renderer.grid_offset[0] + position.x * self.renderer.cell_size
        y = self.renderer.grid_offset[1] + position.y * self.renderer.cell_size
        return (x, y)
    
    def _handle_end_turn_command(self):
        """Termina el turno y limpia estado"""
        try:
            events = self.turn_service.end_player_turn(self.current_battle_id)
            print("🔚 Turno terminado")
            for event in events:
                print(f"📢 {type(event).__name__}")
            
            # Limpiar estado
            self._clear_selection()
            
        except Exception as e:
            print(f"❌ Error al terminar turno: {e}")
    
    def _handle_reset_command(self):
        """Reinicia la batalla"""
        self.current_battle_id = self._create_initial_battle()
        self._clear_selection()
        print("🔄 Batalla reiniciada")