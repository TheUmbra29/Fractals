"""
GAME LOOP COMPLETO - Con sistema de estados y menú contextual
"""
import pygame
from uuid import uuid4

from core.domain.entities.aggregates.battle import Battle
from core.domain.entities.value_objects.game_enums import Team, CharacterClass
from core.domain.entities.battle_entity import BattleEntity
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.stats import EntityStats

from .input_service import InputService
from .enhanced_rendering_service import EnhancedRenderingService
from .game_states import GameState, GameContext
from .action_menu import ActionMenu

class GameLoop:
    """Game Loop completo con sistema de estados y menú contextual"""

    def __init__(self, battle_repository, turn_service):
        self.battle_repo = battle_repository
        self.turn_service = turn_service
        self.input_service = InputService()
        self.renderer = EnhancedRenderingService()
        
        self.current_battle_id = None
        self.running = False
        
        # Contexto del juego y menú
        self.context = GameContext()
        self.action_menu = None
        self.valid_moves = []
        
        print("🎮 Game Loop inicializado - Sistema de estados activo")

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
            clicked_entity = self._get_entity_at_position(battle, target_pos)
            # ✅ ACTUALIZADO: Usar Team enum en lugar de strings
            if (clicked_entity and 
                clicked_entity.team == Team.PLAYER and 
                battle.current_turn == Team.PLAYER):
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
        
        # ✅ SOLO calcular movimientos válidos si NO estamos en modo trazado
        if self.context.current_state == GameState.ENTITY_SELECTED:
            self.valid_moves = self.turn_service.get_valid_moves(
                self.current_battle_id, self.context.selected_entity_id
            )
        
        # Click en el menú de acciones
        if self.input_service.is_mouse_clicked():
            mouse_pos = self.input_service.get_mouse_position()
            selected_action = self.action_menu.handle_click(mouse_pos)
            
            if selected_action:
                self._handle_action_selection(selected_action, selected_entity)
            else:
                # Click fuera del menú - deseleccionar
                self._clear_selection()

    def _handle_input_tracing_route(self):
        """Estado TRACING_ROUTE: Trazado de ruta con cursor libre"""
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
            
            # ACTUALIZAR RUTA EN TIEMPO REAL (sin click mantenido)
            self._update_route_preview(selected_entity, cursor_pos)
            
            # Click: marcar embestida o confirmar movimiento
            if self.input_service.is_mouse_clicked():
                self._handle_route_click(battle, cursor_pos, selected_entity)

    def _handle_input_targeting_ability(self):
        """Estado TARGETING_ABILITY: Seleccionar objetivo para habilidad"""
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
            target_entity = self._get_entity_at_position(battle, target_pos)

            # Validar que haya un objetivo
            if not target_entity:
                print("❌ Debes seleccionar un objetivo válido")
                return

            try:
                # Ejecutar la habilidad
                message = self.turn_service.execute_ability(
                    self.current_battle_id,
                    self.context.selected_entity_id,
                    self.context.pending_action,
                    target_entity.id
                )
                print(f"🔮 {message}")
                self._clear_selection()
                
            except Exception as e:
                print(f"❌ Error al usar habilidad: {e}")

    def _handle_action_selection(self, action_type: str, entity: BattleEntity):
        """Procesa selección de acción - LIMPIAR movimientos válidos al entrar en trazado"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        
        if action_type == "move":
            self.context.current_state = GameState.TRACING_ROUTE
            self.context.pending_action = "move"
            self.action_menu.set_visibility(False)
            
            # ✅ LIMPIAR movimientos válidos para que no se muestre el rango azul
            self.valid_moves = []
            
            print("🛣️ Modo TRAZADO DE RUTA activado")
            print("💡 Mueve el cursor para ver la ruta - Click en enemigos para embestida")

    def _update_route_preview(self, entity: BattleEntity, cursor_pos: Position):
        """Actualiza la previsualización de ruta en tiempo real"""
        if entity.position == cursor_pos:
            self.context.current_route = None
            self.renderer.update_route_preview(None)
            return
        
        try:
            # Calcular ruta hacia la posición del cursor
            route = self.turn_service.calculate_movement_route(
                self.current_battle_id, 
                self.context.selected_entity_id, 
                cursor_pos
            )
            
            # Aplicar embestidas marcadas manualmente
            if route and self.context.marked_dash_targets:
                # Filtrar dash_targets para incluir solo los marcados manualmente
                route.dash_targets = [
                    enemy for enemy in route.dash_targets 
                    if enemy.id in self.context.marked_dash_targets
                ]
            
            self.context.current_route = route
            self.renderer.update_route_preview(route)
            
        except Exception as e:
            self.context.current_route = None
            self.renderer.update_route_preview(None)

    def _handle_route_click(self, battle, click_pos: Position, selected_entity: BattleEntity):
        """Maneja clicks durante el trazado de ruta"""
        clicked_entity = self._get_entity_at_position(battle, click_pos)
        
        if clicked_entity and clicked_entity.team == Team.ENEMY:
            # MARCAR/DESMARCAR embestida manual
            if clicked_entity.id in self.context.marked_dash_targets:
                self.context.marked_dash_targets.remove(clicked_entity.id)
                print(f"❌ Embestida desmarcada: {clicked_entity.name}")
            else:
                self.context.marked_dash_targets.append(clicked_entity.id)
                print(f"🎯 Embestida marcada: {clicked_entity.name}")
                
        else:
            # CONFIRMAR movimiento
            try:
                message = self.turn_service.execute_movement_with_dashes(
                    self.current_battle_id, 
                    self.context.selected_entity_id, 
                    click_pos,
                    self.context.marked_dash_targets  # Pasar embestidas manuales
                )
                print(f"➡️ {message}")
                
                # Volver a estado inicial
                self._clear_selection()
                
            except Exception as e:
                print(f"❌ Error en movimiento: {e}")

    def _execute_basic_attack(self, attacker, target_entity, battle):
        """Ejecuta ataque básico"""
        if not target_entity or target_entity.team != Team.ENEMY:
            print("❌ Objetivo no válido para ataque")
            return

        # Validar que no haya usado ataque este turno
        if not self.context.can_perform_action("basic_attack", attacker):
            print("❌ Ya usaste el ataque básico este turno")
            return

        # Calcular daño (placeholder - luego integraremos DamageCalculationService)
        damage = 25  # Placeholder
        events = target_entity.take_damage(damage)
        
        # Marcar acción como usada
        attacker.mark_action_used("basic_attack")
        
        # Consumir acción del turno
        battle.consume_player_action()
        self.battle_repo.save(battle)
        
        print(f"⚔️ {attacker.name} ataca a {target_entity.name} por {damage} de daño")
        self._clear_selection()

    def _execute_ability(self, caster, target_entity, battle):
        """Ejecuta habilidad (placeholder - PH/TdE vendrá después)"""
        ability_type = self.context.pending_action
        
        # Validar que no haya usado esta habilidad este turno
        if not self.context.can_perform_action(ability_type, caster):
            print(f"❌ Ya usaste {ability_type} este turno")
            return

        # Placeholder - luego integraremos sistema de habilidades
        print(f"🔮 {caster.name} usa {ability_type} en {target_entity.name if target_entity else 'posición'}")
        
        # Marcar acción como usada
        caster.mark_action_used(ability_type)
        
        # Consumir acción del turno
        battle.consume_player_action()
        self.battle_repo.save(battle)
        
        self._clear_selection()

    def _clear_selection(self):
        """Limpia toda la selección y vuelve al estado IDLE"""
        self.context.reset()
        self.action_menu = None
        self.valid_moves = []
        print("🧹 Selección limpiada")

    def _update_game_state(self):
        """Actualiza estado del juego"""
        # Por ahora vacío, la lógica está en los servicios
        pass

    def _render_frame(self):
        """Renderiza el frame con el contexto actual"""
        battle = self.battle_repo.get_by_id(self.current_battle_id)
        
        # Pasar el contexto al renderizador
        self.renderer.set_action_menu(self.action_menu)
        self.renderer.render_battle(battle, self.context, self.valid_moves)

    def _create_initial_battle(self):
        """Crea batalla inicial usando enums"""
        battle_id = uuid4()
        battle = Battle(battle_id, mode="arcade", grid_size=(8, 8))
        player = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(1, 1),
            stats=EntityStats(100, 100, 50, 50, 25, 15, 10),
            team=Team.PLAYER,
            name="Ricchard",
            character_class=CharacterClass.DAMAGE
        )
        enemy = BattleEntity(
            entity_id=EntityId.generate(),
            position=Position(6, 6),
            stats=EntityStats(80, 80, 30, 30, 20, 10, 8),
            team=Team.ENEMY,
            name="Enemy Bot",
            character_class=CharacterClass.DAMAGE
        )
        # Añadir obstáculos desde configuración
        from core.domain.config.game_config import GAME_CONFIG
        for obstacle_pos in GAME_CONFIG.INITIAL_OBSTACLES:
            battle.add_obstacle(Position(obstacle_pos[0], obstacle_pos[1]))
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
            self._clear_selection()
            
        except Exception as e:
            print(f"❌ Error al terminar turno: {e}")

    def _handle_reset_command(self):
        """Reinicia la batalla"""
        self.current_battle_id = self._create_initial_battle()
        self._clear_selection()
        print("🔄 Batalla reiniciada")

    def _position_to_screen(self, position: Position) -> tuple:
        """Convierte posición del grid a coordenadas de pantalla"""
        x = self.renderer.grid_offset[0] + position.x * self.renderer.cell_size
        y = self.renderer.grid_offset[1] + position.y * self.renderer.cell_size
        return (x, y)