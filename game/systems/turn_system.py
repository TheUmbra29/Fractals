class TurnSystem:
    def __init__(self):
        self.current_turn = "player"
        self.turn_count = 1
    
    def start_player_turn(self):
        self.current_turn = "player"
        print(f"=== TURNO {self.turn_count} - JUGADOR ===")
    
    def start_enemy_turn(self):
        self.current_turn = "enemy"
        print(f"=== TURNO {self.turn_count} - ENEMIGO ===")
    
    def end_turn(self):
        if self.current_turn == "player":
            self.start_enemy_turn()
        else:
            self.turn_count += 1
            self.start_player_turn()
    
    def can_select(self, entity):
        return entity.team == self.current_turn and not (entity.has_moved and entity.has_acted)