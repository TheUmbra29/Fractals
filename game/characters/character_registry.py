class CharacterRegistry:
    """Registro central de todos los personajes disponibles"""
    
    _characters = {}
    
    @classmethod
    def register(cls, character_id, character_class):
        """Registra una clase de personaje"""
        cls._characters[character_id] = character_class
        print(f"📝 Registrado: {character_id} -> {character_class.__name__}")
    
    @classmethod
    def get_character_class(cls, character_id):
        """Obtiene la clase de personaje por ID"""
        return cls._characters.get(character_id)
    
    @classmethod
    def get_available_characters(cls):
        """Retorna todos los personajes disponibles"""
        return list(cls._characters.keys())
    
    @classmethod
    def create_character(cls, character_id, position, team="player", **kwargs):
        """Crea una instancia de personaje"""
        character_class = cls.get_character_class(character_id)
        if character_class:
            return character_class(position, team, **kwargs)
        raise ValueError(f"Personaje no encontrado: {character_id}")

# 🆕 CORREGIDO: characters está dentro de game
from game.characters.ricchard import Ricchard
from game.characters.red_thunder import RedThunder  
from game.characters.zoe import Zoe

CharacterRegistry.register("ricchard", Ricchard)
CharacterRegistry.register("red_thunder", RedThunder)
CharacterRegistry.register("zoe", Zoe)