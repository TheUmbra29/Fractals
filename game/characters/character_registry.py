from game.core.config_manager import ConfigManager

class CharacterRegistry:
    """Registro central con imports dinámicos para evitar circularidad"""
    
    _characters = {}
    _config_manager = ConfigManager.get_instance()
    
    @classmethod
    def register_from_config(cls, character_id: str):
        """Registra un personaje usando imports dinámicos"""
        config = cls._config_manager.get_character_config(character_id)
        if not config:
            print(f"❌ No se pudo cargar configuración para: {character_id}")
            return False
        
        try:
            if character_id == "ricchard":
                from .ricchard import Ricchard
                cls._characters[character_id] = Ricchard
            elif character_id == "red_thunder":
                from .red_thunder import RedThunder
                cls._characters[character_id] = RedThunder
            elif character_id == "zoe":
                from .zoe import Zoe
                cls._characters[character_id] = Zoe
            else:
                print(f"❌ Clase no encontrada para: {character_id}")
                return False
                
            print(f"✅ Registrado desde config: {character_id}")
            return True
            
        except ImportError as e:
            print(f"❌ Error importando {character_id}: {e}")
            return False
    
    @classmethod
    def get_character_config(cls, character_id: str):
        """Obtiene la configuración de un personaje"""
        return cls._config_manager.get_character_config(character_id)
    
    @classmethod
    def get_character_class(cls, character_id: str):
        return cls._characters.get(character_id)
    
    @classmethod
    def get_available_characters(cls):
        return list(cls._characters.keys())
    
    @classmethod
    def create_character(cls, character_id: str, position, team="player", **kwargs):
        character_class = cls.get_character_class(character_id)
        if character_class:
            return character_class(position, team, **kwargs)
        raise ValueError(f"Personaje no encontrado: {character_id}")

# ✅ REGISTRO AUTOMÁTICO DESDE CONFIGURACIONES
CharacterRegistry.register_from_config("ricchard")
CharacterRegistry.register_from_config("red_thunder")
CharacterRegistry.register_from_config("zoe")