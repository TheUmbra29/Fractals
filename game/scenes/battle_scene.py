# game/scenes/battle_scene.py
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
                # 🆕 INICIALIZAR SISTEMA DE EFECTOS
        
        # 🆕 SISTEMA DE ESTADOS
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
            # 🆕 INICIALIZAR SISTEMA DE EFECTOS
        self.effect_system = EffectSystem()
        
        # 🆕 CARGAR CONFIGURACIÓN DE EFECTOS
        from game.data.effects import EFFECTS_CONFIG
        self.effect_system.load_effects_config(EFFECTS_CONFIG)
        
    # 🆕 MÉTODO PARA ACCEDER AL EFFECT_SYSTEM DESDE LOS COMPONENTES
    def get_effect_system(self):
        return self.effect_system
    
    def setup_scalable_scenario(self, player_party_ids, enemy_configs):
        """MÉTODO SE MANTIENE IGUAL - no cambios"""
        start_positions = [(2, 2), (2, 4), (2, 6)]
        player_party = CharacterFactory.create_party(
            player_party_ids[:3], start_positions[:len(player_party_ids)]
        )
        
        for character in player_party:
            if hasattr(character, 'register_passives'):
                character.register_passives(self.passive_system)
        
        enemies = [Enemy(config["position"], "enemy", config.get("name", "Enemigo")) 
                  for config in enemy_configs]
        
        self.entities = player_party + enemies
        print(f"✅ Equipo: {[p.name for p in player_party]}")
        print(f"✅ Enemigos: {[e.name for e in enemies]}")
        print("🎯 Estados activos: Idle (selección) | Movement (M) | Ability (H)")
    
    # 🆕 MÉTODOS DE GESTIÓN DE ESTADOS
    def set_state(self, new_state_name):
        """Cambia al estado especificado"""
        if new_state_name not in self.states or self.states[new_state_name] is None:
            print(f"❌ Estado no disponible: {new_state_name}")
            return
        
        if self.current_state.name == new_state_name:
            return
        
        print(f"🔄 Cambiando estado: {self.current_state.name} → {new_state_name}")
        self.current_state.exit()
        self.current_state = self.states[new_state_name]
        self.current_state.enter()
    
    # 🆕 MÉTODOS DELEGADOS A LOS ESTADOS
    def handle_event(self, event):
        """Delega el manejo de eventos al estado actual"""
        if self.ability_menu and self.ability_menu.visible:
            self._handle_ability_menu_event(event)
        else:
            self.current_state.handle_event(event)
    
    def update(self):
        """Delega la actualización al estado actual"""
        self.current_state.update()
    
    def draw(self):
        """Dibuja elementos comunes y delega al estado actual"""
        self.screen.fill((30, 30, 60))
        self.grid.draw(self.screen)
        
        # 🆕 El estado actual dibuja sus elementos específicos
        self.current_state.draw()
        
        # Elementos comunes (siempre se dibujan)
        for entity in self.entities:
            entity.draw(self.screen, self.grid)
        
        if self.ability_menu:
            self.ability_menu.draw()
        
        self.draw_ui()
    
    # 🎯 MÉTODOS DE COMPATIBILIDAD (para estados y código existente)
    def enter_movement_mode(self):
        """Interface para estados - cambia a movimiento"""
        self.set_state("movement")
    
    def open_ability_menu(self):
        """Interface para estados - abre menú de habilidades"""
        if not self.selected_entity or self.selected_entity.has_acted:
            return print("❌ No se puede usar habilidades")
        
        screen_pos = self.grid.get_screen_position(self.selected_entity.position)
        self.ability_menu = AbilityMenu(self.screen, self.selected_entity, screen_pos)
        self.ability_menu.show()
    
    def on_ability_selected(self, ability_data):
        """Interface cuando se selecciona habilidad del menú"""
        print(f"🎯 {self.selected_entity.name} prepara {ability_data['name']}")
        
        if self.ability_system.select_ability(ability_data, self.selected_entity, self.entities):
            self.set_state("ability")
        
        self.ability_menu = None
    
    def clear_selections(self):
        """Limpia selecciones y vuelve a idle"""
        self.selected_entity = None
        self.ability_system.clear_selection()
        self.ability_menu = None
        self.movement_system.cancel()
        self.set_state("idle")
    
    def end_turn(self):
        print("🔄 Terminando turno...")
        self.effect_system.update_effects(self.entities)  # 🆕 ACTUALIZAR EFECTOS
        self.set_state("idle")
        
        for entity in self.entities:
            if entity.team == self.turn_system.current_turn:
                entity.reset_turn()
        
        self.clear_selections()
        self.turn_system.end_turn()
        
        if self.turn_system.current_turn == "enemy":
            self.do_enemy_turn()
    
    def start_turn(self, entity):
        """Llamar al inicio del turno de una entidad"""
        self.effect_system.on_turn_start(entity)  # 🆕 NOTIFICAR EFECTOS
    
    # 🎯 MÉTODOS PRIVADOS QUE SE MANTIENEN
    def _handle_ability_menu_event(self, event):
        """Maneja eventos del menú de habilidades"""
        if event.type == pygame.KEYDOWN:
            result = self.ability_menu.handle_input(event.key)
            if result == "cancel":
                self.ability_menu = None
                print("❌ Menú cancelado")
            elif result:
                self.on_ability_selected(result)
    
    def do_enemy_turn(self):
        """Turno del enemigo - se mantiene igual"""
        print("🤖 Turno del enemigo...")
        for entity in self.entities:
            if entity.team == "enemy" and not entity.has_acted:
                entity.has_acted = True
        
        pygame.time.set_timer(pygame.USEREVENT, 1000)
    
# En game/scenes/battle_scene.py - MÉTODO draw_ui()
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