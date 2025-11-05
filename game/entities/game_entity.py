import pygame

class GameEntity:
    def __init__(self, name, position, team="player", stats=None):
        self.name = name
        self.position = position  # 🆕 CAMBIO: grid_position -> position para consistencia
        self.team = team
        
        # 🆕 SISTEMA DE STATS UNIFICADO - todos usan diccionario
        default_stats = {
            'max_hp': 100,
            'current_hp': 100,
            'max_ph': 100, 
            'current_ph': 100,
            'attack': 15,
            'defense': 8,
            'speed': 5
        }
        
        self.stats = default_stats.copy()
        if stats:
            self.stats.update(stats)  # 🎯 TUS stats únicas REEMPLAZAN los defaults
        
        # Estado del turno
        self.has_moved = False
        self.has_acted = False
        
        # 🆕 SISTEMA DE ACCIONES - requerido por Character
        self.actions = {}
        
        # Visual
        self.color = (0, 255, 0) if team == "player" else (255, 0, 0)
        self.size = 40
    
    def add_action(self, action_key, action_instance):
        """🆕 AGREGADO: Sistema de acciones que Character espera"""
        self.actions[action_key] = action_instance
    
    def perform_action(self, action_key, context):
        """🆕 AGREGADO: Ejecutar acción"""
        if action_key in self.actions:
            return self.actions[action_key].execute(context)
        return False
    
    # 🆕 MÉTODOS COMPATIBILIDAD - para BattleScene existente
    @property
    def grid_position(self):
        return self.position
    
    @grid_position.setter 
    def grid_position(self, value):
        self.position = value
    
    @property
    def current_hp(self):
        return self.stats['current_hp']
    
    @current_hp.setter
    def current_hp(self, value):
        self.stats['current_hp'] = value
    
    @property
    def current_ph(self):
        return self.stats['current_ph']
    
    @current_ph.setter
    def current_ph(self, value):
        self.stats['current_ph'] = value
    
    @property
    def attack(self):
        return self.stats['attack']
    
    @property
    def defense(self):
        return self.stats['defense']
    
    def move_to(self, new_position):
        if not self.has_moved:
            self.position = new_position
            self.has_moved = True
            print(f"🎯 {self.name} se movió a {new_position}")
            return True
        return False
    
    def basic_attack(self, target):
        if not self.has_acted:
            damage = max(1, self.stats['attack'] - target.stats['defense'] // 2)
            target.stats['current_hp'] -= damage
            
            # Regenerar PH
            self.stats['current_ph'] = min(self.stats['max_ph'], self.stats['current_ph'] + 25)
            
            self.has_acted = True
            print(f"⚔️ {self.name} atacó a {target.name} por {damage} daño! +25 PH")
            return True
        return False
    
    def reset_turn(self):
        self.has_moved = False
        self.has_acted = False
    
    def draw(self, screen, grid_system):
        screen_pos = grid_system.get_screen_position(self.position)
        center_x = screen_pos[0] + grid_system.cell_size // 2
        center_y = screen_pos[1] + grid_system.cell_size // 2
        
        # Círculo del personaje
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.size // 2)
        
        # Nombre
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.name, True, (255, 255, 255))
        screen.blit(text, (center_x - text.get_width() // 2, center_y - 30))
        
        # Barra de PH
        ph_width = 30
        ph_ratio = self.stats['current_ph'] / self.stats['max_ph']
        ph_rect = pygame.Rect(center_x - ph_width//2, center_y + 20, ph_width * ph_ratio, 5)
        pygame.draw.rect(screen, (100, 200, 255), ph_rect)