import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_use_cases():
    """Test de casos de uso básicos"""
    print("🧪 TESTEANDO CASOS DE USO...")
    
    try:
        from core.application.use_cases.commands.move_entity_command import MoveEntityCommand
        from core.application.use_cases.commands.execute_ability_command import ExecuteAbilityCommand
        from core.application.use_cases.commands.end_turn_command import EndTurnCommand
        from core.application.use_cases.queries.get_battle_state_query import GetBattleStateQuery
        
        print("✅ Todos los casos de uso importados correctamente")
        
        # Test creación de comandos
        from uuid import uuid4
        from core.domain.entities.value_objects.entity_id import EntityId
        from core.domain.entities.value_objects.position import Position
        from core.domain.entities.value_objects.ability_id import AbilityId
        
        battle_id = uuid4()
        entity_id = EntityId.generate()
        position = Position(3, 3)
        ability_id = AbilityId.generate()
        
        move_command = MoveEntityCommand(battle_id, entity_id, position)
        ability_command = ExecuteAbilityCommand(battle_id, entity_id, ability_id)
        end_turn_command = EndTurnCommand(battle_id)
        state_query = GetBattleStateQuery(battle_id)
        
        print(f"✅ MoveEntityCommand creado: battle={move_command.battle_id}, entity={move_command.entity_id}")
        print(f"✅ ExecuteAbilityCommand creado: ability={ability_command.ability_id}")
        print(f"✅ EndTurnCommand creado: battle={end_turn_command.battle_id}")
        print(f"✅ GetBattleStateQuery creado: battle={state_query.battle_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en casos de uso: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎮 TESTEO DE CASOS DE USO FRACTALS")
    print("=" * 50)
    
    success = test_use_cases()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ¡CASOS DE USO LISTOS PARA CONTINUAR!")
        print("Próximo paso: Infraestructura (repositorios)")
    else:
        print("🔧 Hay problemas en los casos de uso")