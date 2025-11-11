from core.domain.entities.value_objects.game_enums import Team, CharacterClass
from core.domain.entities.value_objects.position import Position
from core.domain.entities.value_objects.stats import EntityStats
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.battle_entity import BattleEntity

# Crear entidades como en el juego
ricchard = BattleEntity(
    entity_id=EntityId.generate(),
    position=Position(1, 1),
    stats=EntityStats(100, 100, 50, 50, 25, 15, 10),
    team=Team.PLAYER,
    name="Ricchard",
    character_class=CharacterClass.DAMAGE
)
enemy = BattleEntity(
    entity_id=EntityId.generate(),
    position=Position(6, 6),
    stats=EntityStats(80, 80, 30, 30, 20, 10, 8),
    team=Team.ENEMY,
    name="Enemy Bot",
    character_class=CharacterClass.DAMAGE
)

# Simular ciclo de renderizado
for entity in [ricchard, enemy]:
    print(f"[DEBUG] Renderizando entidad: name={entity.name}, id={entity.id}, team={repr(entity.team)}, type={type(entity.team)}")
    is_player = entity.team == Team.PLAYER or (isinstance(entity.team, str) and entity.team.upper() == "PLAYER")
    print(f"  ¿Se pinta azul? {is_player}")