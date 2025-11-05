import pygame
from game.systems.action_system.base_action import ActionContext
from game.systems.selection_system import SelectionSystem

class AbilitySystem:
    def __init__(self, grid_system):
        self.grid_system = grid_system
        self.selected_ability = None
        self.caster = None
        self.selection_system = SelectionSystem(self)
    
    def select_ability(self, ability_data, caster, entities):
        if caster.has_acted:
            print("❌ Ya has actuado este turno")
            return False
        
        if caster.stats['current_ph'] < ability_data['cost_ph']:
            print(f"❌ PH insuficiente: {caster.stats['current_ph']}/{ability_data['cost_ph']}")
            return False
        
        self.selected_ability = ability_data
        self.caster = caster
        
        selection_mode = ability_data.get('selection_mode', 'enemy')
        success = self.selection_system.activate_mode(selection_mode, ability_data, caster, entities)
        
        if success:
            print(f"🎯 Modo {selection_mode.upper()} activado para {ability_data['name']}")
            return True
        else:
            print(f"❌ No se pudo activar el modo {selection_mode}")
            self.clear_selection()
            return False
    
    def create_context(self, target_entity=None, target_position=None):
        return ActionContext(
            caster=self.caster,
            target=target_entity,
            target_position=target_position,
            entities=[]
        )
    
    def execute_ability_directly(self, context):
        if not self.selected_ability or not self.caster:
            return False
        
        ability_key = self.selected_ability['key']
        if ability_key in self.caster.actions:
            success = self.caster.perform_action(ability_key, context)
            if success:
                print(f"🎯 {self.caster.name} usó {self.selected_ability['name']}!")
                self.clear_selection()
                return True
        
        return False
    
    def handle_click(self, grid_pos, entities):
        return self.selection_system.handle_click(grid_pos, entities)
    
    def draw_target_indicators(self, screen):
        self.selection_system.draw_indicators(screen)
    
    def cancel_selection(self):
        return self.selection_system.cancel_selection()
    
    def clear_selection(self):
        self.selected_ability = None
        self.caster = None
        self.selection_system.cancel_selection()
    
    def is_selecting(self):
        return self.selection_system.is_active()
    
    def get_selection_mode(self):
        return self.selection_system.get_current_mode_type()