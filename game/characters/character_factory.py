# 🆕 CORREGIDO: characters está dentro de game
from game.characters.character_registry import CharacterRegistry

class CharacterFactory:
    """Factory para crear personajes de forma escalable"""
    
    @staticmethod
    def create_character(character_id, position, team="player", **kwargs):
        """Crea un personaje por ID"""
        return CharacterRegistry.create_character(character_id, position, team, **kwargs)
    
    @staticmethod
    def create_party(character_ids, start_positions, team="player"):
        """Crea un grupo de personajes (máximo 3 para tu equipo)"""
        if len(character_ids) > 3:
            raise ValueError("El equipo no puede tener más de 3 personajes")
        if len(character_ids) != len(start_positions):
            raise ValueError("Cantidad de IDs y posiciones no coincide")
        
        party = []
        for char_id, position in zip(character_ids, start_positions):
            party.append(CharacterFactory.create_character(char_id, position, team))
        
        return party
    
    @staticmethod
    def get_character_info(character_id):
        """Obtiene información de un personaje sin crearlo (para UI de selección)"""
        char_class = CharacterRegistry.get_character_class(character_id)
        if char_class:
            temp_char = char_class((0, 0), "player")
            return {
                'name': temp_char.name,
                'class': temp_char.character_class,
                'stats': temp_char.stats.copy(),
                'abilities': list(temp_char.actions.keys())
            }
        return None