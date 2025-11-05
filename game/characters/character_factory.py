# game/characters/character_factory.py
from game.entities.battle_entity import BattleEntity  # 🆕 NUEVA IMPORTACIÓN
from .character_registry import CharacterRegistry

class CharacterFactory:
    @staticmethod
    def create_character(character_id, position, team="player", **kwargs):
        """Crea un personaje - compatible con BattleEntity"""
        return CharacterRegistry.create_character(character_id, position, team, **kwargs)
    
    @staticmethod
    def create_party(character_ids, positions, team="player"):
        """Crea un grupo de personajes"""
        party = []
        for char_id, position in zip(character_ids, positions):
            party.append(CharacterFactory.create_character(char_id, position, team))
        return party