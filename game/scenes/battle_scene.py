import pygame
from game.systems.grid_system import GridSystem
from game.systems.turn_system import TurnSystem
from game.systems.ability_system import AbilitySystem
from game.systems.effect_system import EffectSystem
from game.systems.passive_system import PassiveSystem
from game.systems.movement_system import MovementSystem
from game.ui.ability_menu import AbilityMenu
from game.characters.character_factory import CharacterFactory
from game.entities.enemy import Enemy
from game.scenes.battle_states.idle_state import IdleState
from game.scenes.battle_states.movement_state import MovementState
from game.scenes.battle_states.ability_state import AbilityState
from game.scenes.battle_states.menu_state import MenuState
from game.scenes.battle_states.targeting_state import TargetingState
from game.core.logger import logger

class BattleScene:
    def __init__(self, screen, player_party_ids=None, enemy_configs=None):
        self.screen = screen
        self.grid = GridSystem()
        self.turn_system = TurnSystem()
        self.ability_system = AbilitySystem(self.grid)
        self.effect_system = EffectSystem()
        self.passive_system = PassiveSystem()
        self.movement_system = MovementSystem(self.grid)
        self.entities = []
        self.selected_entity = None
        self.ability_menu = None
        
        logger.info("BattleScene inicializando", {"screen_size": screen.get_size()})
        
        # ✅ INICIALIZAR SISTEMA DE EFECTOS
        self.effect_system = EffectSystem()
        
        # ✅ CARGAR CONFIGURACIÓN DE EFECTOS
        from game.data.effects import EFFECTS_CONFIG
        self.effect_system.load_effects_config(EFFECTS_CONFIG)
        logger.debug("Sistema de efectos cargado", {"effects_count": len(EFFECTS_CONFIG)})
        
        # ✅ SISTEMA DE ESTADOS
        self.states = {
            "idle": IdleState(self),
            "movement": MovementState(self), 
            "ability": AbilityState(self),
            "menu": MenuState(self, "pause"), 
            "targeting": None 
        }
        self.current_state = self.states["idle"]
        self.current_state.enter()
        
        # Configuración inicial
        player_party_ids = player_party_ids or ["ricchard", "red_thunder", "zoe"]
        enemy_configs = enemy_configs or [
            {"position": (7, 3), "name": "Orco"}, {"position": (7, 5), "name": "Goblin"}
        ]
        
        self.setup_scalable_scenario(player_party_ids, enemy_configs)
        self.turn_system.start_player_turn()
        logger.info("Escenario de batalla configurado y listo")
    
    # ✅ MÉTODO PARA ACCEDER AL EFFECT_SYSTEM DESDE LOS COMPONENTES
    def get_effect_system(self):
        return self.effect_system
    
    def setup_scalable_scenario(self, player_party_ids, enemy_configs):
        """MÉTODO SE MANTIENE IGUAL - con logging mejorado"""
        try:
            start_positions = [(2, 2), (2, 4), (2, 6)]
            player_party = CharacterFactory.create_party(
                player_party_ids[:3], start_positions[:len(player_party_ids)]
            )
            
            for character in player_party:
                if hasattr(character, 'register_passives'):
                    character.register_passives(self.passive_system)
                # ✅ CONECTAR BATTLE_SCENE A LAS ENTIDADES
                character.battle_scene = self
            
            enemies = [Enemy(config["position"], "enemy", config.get("name", "Enemigo")) 
                      for config in enemy_configs]
            
            self.entities = player_party + enemies
            
            logger.info(
                "Escenario configurado",
                {
                    "equipo": [p.name for p in player_party],
                    "enemigos": [e.name for e in enemies],
                    "total_entidades": len(self.entities)
                }
            )
            
        except Exception as e:
            logger.error("Error configurando escenario", exception=e)
            # Fallback básico
            self.entities = []
    
    # ✅ MÉTODOS DE GESTIÓN DE ESTADOS CON MANEJO DE ERRORES
    def set_state(self, new_state_name):
        """Cambia al estado especificado - CON MANEJO DE ERRORES"""
        try:
            if new_state_name not in self.states or self.states[new_state_name] is None:
                logger.warning(f"Estado no disponible: {new_state_name}")
                return
            
            if self.current_state.name == new_state_name:
                return
            
            logger.state_change(
                self.current_state.name, 
                new_state_name, 
                self.selected_entity
            )
            
            self.current_state.exit()
            self.current_state = self.states[new_state_name]
            self.current_state.enter()
            
        except Exception as e:
            logger.error(
                f"Error crítico cambiando estado a {new_state_name}",
                exception=e,
                context={
                    "estado_actual": self.current_state.name,
                    "nuevo_estado": new_state_name
                }
            )
            # Fallback seguro
            if "idle" in self.states and self.states["idle"] is not None:
                self.current_state = self.states["idle"]
                self.current_state.enter()
    
    # ✅ MÉTODOS DELEGADOS A LOS ESTADOS CON LOGGING
    def handle_event(self, event):
        """Delega el manejo de eventos al estado actual"""
        try:
            if self.ability_menu and self.ability_menu.visible:
                self._handle_ability_menu_event(event)
            else:
                self.current_state.handle_event(event)
        except Exception as e:
            logger.error(
                "Error manejando evento",
                exception=e,
                context={
                    "event_type": event.type,
                    "estado_actual": self.current_state.name
                }
            )
    
    def update(self):
        """Delega la actualización al estado actual"""
        try:
            self.current_state.update()
        except Exception as e:
            logger.error(
                "Error en update del estado actual",
                exception=e,
                context={"estado_actual": self.current_state.name}
            )
    
    def draw(self):
        """Dibuja elementos comunes y delega al estado actual"""
        try:
            self.screen.fill((30, 30, 60))
            self.grid.draw(self.screen)
            
            # ✅ El estado actual dibuja sus elementos específicos
            self.current_state.draw()
            
            # Elementos comunes (siempre se dibujan)
            for entity in self.entities:
                entity.draw(self.screen, self.grid)
            
            if self.ability_menu:
                self.ability_menu.draw()
            
            self.draw_ui()
            
        except Exception as e:
            logger.error("Error crítico en draw", exception=e)
            # Intentar recuperación básica
            self.screen.fill((255, 0, 0))  # Fondo rojo de error
            font = pygame.font.SysFont(None, 36)
            error_text = font.render("ERROR EN DIBUJADO", True, (255, 255, 255))
            self.screen.blit(error_text, (100, 100))
    
    # ✅ MÉTODOS DE COMPATIBILIDAD MEJORADOS
    def open_ability_menu(self):
        """Interface para estados - abre menú de habilidades"""
        if not self.selected_entity or self.selected_entity.has_acted:
            logger.warning("Intento de abrir menú de habilidades sin entidad válida")
            return
        
        try:
            screen_pos = self.grid.get_screen_position(self.selected_entity.position)
            self.ability_menu = AbilityMenu(self.screen, self.selected_entity, screen_pos)
            self.ability_menu.show()
            logger.debug("Menú de habilidades abierto", {"entidad": self.selected_entity.name})
        except Exception as e:
            logger.error("Error abriendo menú de habilidades", exception=e)
    
    def on_ability_selected(self, ability_data):
        """Interface cuando se selecciona habilidad del menú"""
        try:
            logger.info(
                f"{self.selected_entity.name} prepara {ability_data['name']}",
                {
                    "ability": ability_data['name'],
                    "cost_ph": ability_data.get('cost_ph', 0),
                    "selection_mode": ability_data.get('selection_mode', 'enemy')
                }
            )
            
            # ✅ Usar el nuevo contexto con effect_system
            context = self.create_ability_context(self.selected_entity)
            
            if self.ability_system.select_ability(ability_data, self.selected_entity, self.entities):
                self.set_state("ability")
            
            self.ability_menu = None
            
        except Exception as e:
            logger.error(
                "Error seleccionando habilidad del menú",
                exception=e,
                context={
                    "entidad": self.selected_entity.name,
                    "habilidad": ability_data['name']
                }
            )
            self.ability_menu = None
    
    def clear_selections(self):
        """Limpia selecciones y vuelve a idle"""
        try:
            self.selected_entity = None
            self.ability_system.clear_selection()
            self.ability_menu = None
            self.movement_system.cancel()
            self.set_state("idle")
            logger.debug("Selecciones limpiadas")
        except Exception as e:
            logger.error("Error limpiando selecciones", exception=e)
    
    def end_turn(self):
        """Termina el turno actual con logging"""
        try:
            logger.info("Terminando turno...", {"turno_actual": self.turn_system.current_turn})
            
            self.effect_system.update_effects(self.entities)
            self.set_state("idle")
            
            for entity in self.entities:
                if entity.team == self.turn_system.current_turn:
                    entity.reset_turn()
            
            self.clear_selections()
            self.turn_system.end_turn()
            
            if self.turn_system.current_turn == "enemy":
                self.do_enemy_turn()
                
        except Exception as e:
            logger.error("Error terminando turno", exception=e)
    
    # ✅ MÉTODOS PRIVADOS MEJORADOS
    def _handle_ability_menu_event(self, event):
        """Maneja eventos del menú de habilidades con logging"""
        try:
            if event.type == pygame.KEYDOWN:
                result = self.ability_menu.handle_input(event.key)
                if result == "cancel":
                    self.ability_menu = None
                    logger.debug("Menú de habilidades cancelado")
                elif result:
                    self.on_ability_selected(result)
        except Exception as e:
            logger.error("Error manejando evento del menú de habilidades", exception=e)
    
    def do_enemy_turn(self):
        """Turno del enemigo - con logging"""
        try:
            logger.info("Iniciando turno del enemigo...")
            
            for entity in self.entities:
                if entity.team == "enemy" and not entity.has_acted:
                    entity.has_acted = True
            
            pygame.time.set_timer(pygame.USEREVENT, 1000)
            logger.debug("Timer de turno enemigo configurado")
            
        except Exception as e:
            logger.error("Error en turno del enemigo", exception=e)

    def draw_ui(self):
        """UI común - ACTUALIZADO para state pattern"""
        font = pygame.font.SysFont(None, 36)
        small_font = pygame.font.SysFont(None, 24)
        
        # Información del turno (se mantiene igual)
        turn_text = f"Turno: {self.turn_system.current_turn} ({self.turn_system.turn_count})"
        self.screen.blit(font.render(turn_text, True, (255, 255, 255)), (20, 20))
        
        # Información del personaje seleccionado (se mantiene igual)
        if self.selected_entity:
            current_energy = self.selected_entity.get_energy_absolute()
            max_energy = self.selected_entity.energy_stats['max_energy']
            energy_percentage = self.selected_entity.get_energy_percentage()
            
            info_lines = [
                f"Seleccionado: {self.selected_entity.name}",
                f"Movimiento: {'✅' if not self.selected_entity.has_moved else '❌'}",
                f"Acción: {'✅' if not self.selected_entity.has_acted else '❌'}",
                f"PH: {self.selected_entity.stats['current_ph']}/{self.selected_entity.stats['max_ph']}",
                f"HP: {self.selected_entity.stats['current_hp']}/{self.selected_entity.stats['max_hp']}",
                f"Energía: {current_energy}/{max_energy}",
                f"Rango Mov: {getattr(self.selected_entity, 'movement_range', 3)}",
                f"Estado: {self.current_state.name.upper()}"  # 🆕 Muestra el estado actual
            ]
            
            # Barra de energía (se mantiene igual)
            energy_width = 200
            energy_fill = int(energy_width * (energy_percentage / 100))
            
            pygame.draw.rect(self.screen, (50, 50, 50), (20, 210, energy_width, 20))
            energy_color = (100, 200, 255)
            if energy_percentage >= 100:
                energy_color = (255, 215, 0)
            pygame.draw.rect(self.screen, energy_color, (20, 210, energy_fill, 20))
            pygame.draw.rect(self.screen, (200, 200, 200), (20, 210, energy_width, 20), 2)
            
            energy_text = f"ENERGÍA: {current_energy}/{max_energy}"
            if energy_percentage >= 100:
                energy_text += " - ULTIMATE LISTA! 💥"
            self.screen.blit(small_font.render(energy_text, True, (255, 255, 255)), (25, 212))
            
            # Ultimate costos (se mantiene igual)
            ultimate_cost = None
            ultimate_name = None
            for ability_key, ability_config in self.selected_entity.abilities_config.items():
                if ability_config.get('is_ultimate', False):
                    ultimate_cost = ability_config.get('energy_cost', 100)
                    ultimate_name = ability_config.get('name', 'Ultimate')
                    break
            
            if ultimate_cost:
                cost_text = f"Ultimate: {ultimate_name} - Costo: {ultimate_cost}"
                cost_color = (100, 255, 100) if current_energy >= ultimate_cost else (255, 100, 100)
                self.screen.blit(small_font.render(cost_text, True, cost_color), (25, 235))
            
            # Dibujar líneas de info
            for i, text in enumerate(info_lines):
                self.screen.blit(small_font.render(text, True, (255, 255, 255)), (20, 60 + i * 25))
        
        # 🆕 INSTRUCCIONES DEL ESTADO ACTUAL
        instructions = self.current_state.get_instructions()
        for i, instruction in enumerate(instructions):
            self.screen.blit(small_font.render(instruction, True, (150, 200, 255)), 
                        (20, 500 + i * 30))
            
    def open_menu(self, menu_type="pause"):
        """Abre el menú de pausa/inventario"""
        self.states["menu"] = MenuState(self, menu_type)
        self.set_state("menu")
    
    def start_targeting(self, ability_data, targeting_type="area"):
        """Inicia selección avanzada de objetivos"""
        self.states["targeting"] = TargetingState(self, ability_data, targeting_type)
        self.set_state("targeting")

    def create_ability_context(self, caster, target=None, target_position=None, entities=None):
        """Crea contexto para habilidades incluyendo effect_system - VERSIÓN MEJORADA"""
        from game.core.action_base import ActionContext
        
        # Usar las entidades proporcionadas o las de la escena
        context_entities = entities if entities is not None else self.entities
        
        context = ActionContext(
            caster=caster,
            target=target,
            target_position=target_position,
            entities=context_entities
        )
        
        # ✅ Asegurar que el context tenga effect_system y battle_scene
        if not hasattr(context, 'extra_data'):
            context.extra_data = {}
        
        context.extra_data.update({
            'effect_system': self.effect_system,
            'battle_scene': self,
            'turn_system': self.turn_system
        })
        
        logger.debug(
            "Contexto de habilidad creado", 
            {
                "caster": caster.name,
                "target": target.name if target else "None", 
                "target_position": target_position,
                "entities_count": len(context_entities)
            }
        )
        
        return context