from abc import ABC, abstractmethod
from typing import Tuple, List, Callable

class InputPort(ABC):
    """Puerto de entrada - abstracción para manejar input del usuario"""
    
    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        pass
    
    @abstractmethod
    def is_mouse_clicked(self) -> bool:
        pass
    
    @abstractmethod
    def get_key_events(self) -> List[str]:
        pass
    
    @abstractmethod
    def process_events(self) -> None:
        pass
    
    @abstractmethod
    def subscribe(self, observer: Callable) -> None:
        pass