from abc import ABC, abstractmethod
from typing import Dict, Any

class RenderingPort(ABC):
    """Puerto de renderizado - abstracción para mostrar el juego"""
    
    @abstractmethod
    def initialize(self) -> None:
        pass
    
    @abstractmethod
    def render_battle(self, battle_state: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        pass