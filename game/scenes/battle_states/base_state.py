# game/scenes/battle_states/base_state.py
from abc import ABC, abstractmethod
import pygame

class BattleState(ABC):
    """Estado base abstracto para la máquina de estados de BattleScene"""
    
    def __init__(self, battle_scene):
        self.battle_scene = battle_scene
        self.name = self.__class__.__name__
    
    @abstractmethod
    def enter(self):
        """Llamado cuando se entra al estado"""
        pass
    
    @abstractmethod
    def exit(self):
        """Llamado cuando se sale del estado"""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """Maneja eventos de pygame"""
        pass
    
    @abstractmethod
    def update(self):
        """Actualiza lógica del estado"""
        pass
    
    @abstractmethod
    def draw(self):
        """Dibuja elementos específicos del estado"""
        pass
    
    def get_instructions(self):
        """Instrucciones para mostrar en UI - puede ser override"""
        return []