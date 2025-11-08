import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    _instance = None
    _config_cache = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance
    
    def _find_config_file(self, character_id: str) -> str:
        """Busca el archivo de configuración en las ubicaciones correctas"""
        possible_paths = [
            # TU ESTRUCTURA ACTUAL - archivos en game/characters/
            f"game/characters/{character_id}.json",
            # Otras ubicaciones por si acaso
            f"./game/characters/{character_id}.json",
            f"{os.getcwd()}/game/characters/{character_id}.json",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"🔍 Encontrado: {path}")
                return path
            else:
                print(f"❌ No existe: {path}")
        
        return None
    
    def get_character_config(self, character_id: str) -> Dict[str, Any]:
        cache_key = f"character_{character_id}"
        
        if cache_key not in self._config_cache:
            file_path = self._find_config_file(character_id)
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self._config_cache[cache_key] = config
                    print(f"✅ Config cargada: {character_id} desde {file_path}")
                except Exception as e:
                    print(f"❌ Error cargando {file_path}: {e}")
                    self._config_cache[cache_key] = self._create_fallback_config(character_id)
            else:
                print(f"❌ No se encontró archivo de configuración para: {character_id}")
                self._config_cache[cache_key] = self._create_fallback_config(character_id)
        
        return self._config_cache[cache_key].copy()
    
    def _create_fallback_config(self, character_id: str) -> Dict[str, Any]:
        """Crea una configuración básica si no se encuentra el archivo"""
        print(f"⚠️  Usando configuración de respaldo para {character_id}")
        
        fallback_configs = {
            "ricchard": {
                "id": "ricchard",
                "name": "Ricchard",
                "character_class": "damage",
                "stats": {
                    "max_hp": 100, "current_hp": 100,
                    "max_ph": 130, "current_ph": 130,
                    "attack": 100, "defense": 40, "speed": 20, "max_energy": 120
                },
                "energy_sources": {
                    "on_hit": {"base": 10, "type": "flat"},
                    "on_take_damage": {"base": 8, "type": "flat"},
                    "on_ability_use": {"base": 12, "type": "flat"},
                    "on_kill": {"base": 30, "type": "flat"},
                    "per_turn": {"base": 8, "type": "flat"},
                    "on_void_ability": {"base": 15, "type": "flat"}
                },
                "abilities": {}
            },
            "red_thunder": {
                "id": "red_thunder",
                "name": "Red Thunder", 
                "character_class": "tank",
                "stats": {
                    "max_hp": 90, "current_hp": 90,
                    "max_ph": 100, "current_ph": 100, 
                    "attack": 90, "defense": 30, "speed": 18, "max_energy": 100
                },
                "energy_sources": {
                    "on_hit": {"base": 12, "type": "flat"},
                    "on_take_damage": {"base": 6, "type": "flat"},
                    "on_ability_use": {"base": 15, "type": "flat"},
                    "on_kill": {"base": 25, "type": "flat"},
                    "per_turn": {"base": 8, "type": "flat"},
                    "on_storm_ability": {"base": 20, "type": "flat"}
                },
                "abilities": {}
            },
            "zoe": {
                "id": "zoe",
                "name": "Zoe",
                "character_class": "support", 
                "stats": {
                    "max_hp": 100, "current_hp": 100,
                    "max_ph": 150, "current_ph": 150,
                    "attack": 80, "defense": 40, "speed": 11, "max_energy": 120
                },
                "energy_sources": {
                    "on_hit": {"base": 8, "type": "flat"},
                    "on_take_damage": {"base": 5, "type": "flat"},
                    "on_ability_use": {"base": 10, "type": "flat"},
                    "on_kill": {"base": 20, "type": "flat"},
                    "per_turn": {"base": 6, "type": "flat"},
                    "on_light_ability": {"base": 12, "type": "flat"},
                    "on_ally_attack": {"base": 10, "type": "flat"}
                },
                "abilities": {}
            }
        }
        
        return fallback_configs.get(character_id, {})
    
    def get_effect_config(self, effect_id: str) -> Dict[str, Any]:
        if "effects" not in self._config_cache:
            effects_path = "game/data/effects.json"
            self._config_cache["effects"] = self._load_json_file(effects_path)
        
        return self._config_cache["effects"].get(effect_id, {}).copy()
    
    def get_all_effects(self) -> Dict[str, Any]:
        if "effects" not in self._config_cache:
            effects_path = "game/data/effects.json"
            self._config_cache["effects"] = self._load_json_file(effects_path)
        
        return self._config_cache["effects"].copy()
    
    def _load_json_file(self, file_path: str) -> Dict[str, Any]:
        """Carga un archivo JSON con manejo de errores"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Archivo no encontrado: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error en JSON {file_path}: {e}")
            return {}