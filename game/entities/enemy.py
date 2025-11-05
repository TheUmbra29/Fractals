from game.entities.character import Character

class Enemy(Character):
    """Enemigo básico del juego"""
    
    def __init__(self, position, team="enemy", name=None):
        stats = {
            'max_hp': 60,
            'current_hp': 60,
            'max_ph': 80,
            'current_ph': 80,
            'attack': 12,
            'defense': 6,
            'speed': 4
        }
        
        super().__init__(
            name=name or "Enemigo",
            position=position,
            team=team,
            stats=stats
            # ⬆️ ELIMINA 'role' - la clase Character no lo necesita
        )