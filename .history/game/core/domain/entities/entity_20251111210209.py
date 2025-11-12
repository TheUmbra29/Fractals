from typing import List
from game.core.domain.entities.value_objects.position import Position
from game.core.domain.entities.value_objects.stats import EntityStats
from game.core.domain.services.cover_system import CoverSystem, CoverType

class Entity:
	def __init__(self, id: str, name: str, position: Position, team: str, stats: EntityStats):
		self.id = id
		self.name = name
		self.position = position
		self.team = team
		self.stats = stats
		self.is_covered = False
		self.cover_type = None
    
	def update_cover_status(self, cover_system: CoverSystem, enemies: List['Entity']):
		"""Actualiza el estado de cobertura basado en enemigos cercanos y estructuras"""
		self.is_covered = False
		self.cover_type = None
		for enemy in enemies:
			if enemy.team != self.team:
				cover_status = cover_system.get_cover_status(enemy.position, self.position)
				if cover_status != CoverType.FULL:  # Si hay alguna cobertura
					self.is_covered = True
					self.cover_type = cover_status
					break  # Solo necesitamos un enemigo para determinar cobertura
