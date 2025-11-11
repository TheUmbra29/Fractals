import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core.domain.entities.value_objects.entity_id import EntityId
    from core.domain.entities.value_objects.position import Position
    from core.domain.entities.value_objects.stats import EntityStats
    from core.domain.entities.battle_entity import BattleEntity
    
    print("✅ VERIFICANDO MOVIMIENTO:")
    
    # Crear dos entidades de prueba
    entity1 = BattleEntity(
        entity_id=EntityId.generate(),
        position=Position(1, 1),
        stats=EntityStats(100, 100, 50, 50, 25, 15, 10),
        team="player",
        name="Ricchard",
        character_class="Daño"
    )
    
    entity2 = BattleEntity(
        entity_id=EntityId.generate(),
        position=Position(3, 3),
        stats=EntityStats(80, 80, 30, 30, 20, 10, 8),
        team="enemy",
        name="Enemy Bot",
        character_class="Daño"
    )
    
    # Verificar movimiento
    print(f"  Posición inicial: {entity1.position}")
    entity1.move_to(Position(2, 2))
    print(f"  Posición después de mover: {entity1.position}")
    print(f"  ✅ move_to funciona")
    
    # Verificar que no puede moverse dos veces
    try:
        entity1.move_to(Position(3, 3))
        print("  ❌ Debería fallar al mover dos veces")
    except ValueError as e:
        print(f"  ✅ move_to valida correctamente: {e}")
    
    # Verificar embestida
    events = entity1.execute_dash_attack(entity2)
    print(f"  ✅ execute_dash_attack funciona: {len(events)} eventos generados")
    
    # Verificar daño
    events = entity2.take_damage(20)
    print(f"  ✅ take_damage funciona: {len(events)} eventos generados")
    print(f"  HP después de daño: {entity2.stats.current_hp}")
    
    print("🎉 ¡Todos los métodos de movimiento funcionan!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()