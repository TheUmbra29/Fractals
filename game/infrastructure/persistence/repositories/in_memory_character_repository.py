from typing import Dict, List, Optional
from characters.domain.repositories.character_repository import CharacterRepository
from characters.domain.entities.character import Character

class InMemoryCharacterRepository(CharacterRepository):
    """Repositorio en memoria para characters"""
    
    def __init__(self):
        self._characters: Dict[str, Character] = {}
    
    def get_by_id(self, character_id: str) -> Optional[Character]:
        return self._characters.get(character_id)
    
    def save(self, character: Character) -> None:
        self._characters[character.id] = character
    
    def get_all(self) -> List[Character]:
        return list(self._characters.values())
    
    def get_by_class(self, character_class: str) -> List[Character]:
        return [char for char in self._characters.values() 
                if char.character_class == character_class]