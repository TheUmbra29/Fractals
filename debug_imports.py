# debug_habilities_detallado.py
#!/usr/bin/env python3
"""
Diagnóstico DETALLADO del sistema de habilidades
"""
import sys
import os
sys.path.append('.')

def test_habilidad_especifica(character_name, ability_key):
    """Test individual de una habilidad específica"""
    print(f"\n🔍 TESTEANDO {character_name} -> {ability_key}")
    
    try:
        from game.characters.character_registry import CharacterRegistry
        from game.core.action_base import ActionContext
        
        # Crear personaje
        character = CharacterRegistry.create_character(character_name, (0, 0))
        
        if ability_key not in character.actions:
            print(f"❌ Habilidad {ability_key} no encontrada en {character.name}")
            return False
        
        ability = character.actions[ability_key]
        print(f"✅ Habilidad encontrada: {ability.name}")
        print(f"   - Costo PH: {ability.cost_ph}")
        print(f"   - Rango: {ability.range}")
        print(f"   - Modo selección: {ability.selection_mode}")
        print(f"   - Cooldown: {ability.cooldown}")
        
        # Crear objetivos de prueba
        class MockTarget:
            def __init__(self, name="Target", team="enemy", position=(1,1)):
                self.name = name
                self.team = team
                self.position = position
                self.stats = {
                    'max_hp': 100, 'current_hp': 100,
                    'max_ph': 50, 'current_ph': 50,
                    'attack': 10, 'defense': 5, 'speed': 5
                }
                self.has_moved = False
                self.has_acted = False
                self.actions = {}
        
        # Configurar contexto según el modo de selección
        if ability.selection_mode == "enemy":
            target = MockTarget("Enemigo", "enemy", (1, 0))
            context = ActionContext(caster=character, target=target, entities=[character, target])
        
        elif ability.selection_mode == "chain":
            targets = [
                MockTarget("Enemigo1", "enemy", (1, 0)),
                MockTarget("Enemigo2", "enemy", (2, 0)),
                MockTarget("Enemigo3", "enemy", (3, 0))
            ]
            context = ActionContext(caster=character, entities=targets)
        
        elif ability.selection_mode == "position":
            context = ActionContext(caster=character, target_position=(3, 3), entities=[character])
        
        elif ability.selection_mode == "line":
            context = ActionContext(caster=character, entities=[])
            context.extra_data = {'direction': (1, 0), 'line_length': 3}
        
        elif ability.selection_mode == "aoe":
            targets = [
                MockTarget("Enemigo1", "enemy", (1, 0)),
                MockTarget("Enemigo2", "enemy", (1, 1)),
            ]
            context = ActionContext(caster=character, entities=targets)
        
        else:  # self, none, etc.
            context = ActionContext(caster=character, entities=[character])
        
        # Verificar si puede ejecutarse
        can_execute = ability.can_execute(context)
        print(f"   - Puede ejecutarse: {can_execute}")
        
        if can_execute:
            # Estado antes
            hp_antes = [t.stats['current_hp'] for t in context.entities] if context.entities else [character.stats['current_hp']]
            ph_antes = character.stats['current_ph']
            
            # Ejecutar
            success = ability.execute(context)
            print(f"   - Éxito ejecución: {success}")
            
            # Estado después
            if success:
                hp_despues = [t.stats['current_hp'] for t in context.entities] if context.entities else [character.stats['current_hp']]
                ph_despues = character.stats['current_ph']
                
                print(f"   - PH: {ph_antes} -> {ph_despues} (costo: {ability.cost_ph})")
                
                if hp_antes != hp_despues:
                    print(f"   - Cambio HP: {hp_antes} -> {hp_despues}")
                else:
                    print(f"   - Sin cambio en HP")
            else:
                print(f"   - ❌ La ejecución falló")
        else:
            print(f"   - ❌ No se puede ejecutar (razones arriba)")
        
        return can_execute and success
        
    except Exception as e:
        print(f"❌ Error testeando {ability_key}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_todas_habilidades():
    """Testea todas las habilidades de todos los personajes"""
    print("🎯 DIAGNÓSTICO COMPLETO DE HABILIDADES")
    
    test_cases = [
        ("ricchard", "basic_attack"),
        ("ricchard", "corte_fugaz"), 
        ("ricchard", "destello_vacuo"),
        ("ricchard", "rayo_vacio"),
        ("red_thunder", "basic_attack"),
        ("red_thunder", "carrera_relampago"),
        ("red_thunder", "red_thunderblast"),
        ("red_thunder", "red_storm"),
        ("zoe", "basic_attack"),
        ("zoe", "torbellino_fe"),
        ("zoe", "grito_tempestad"),
        ("zoe", "dawn_cataclysm"),
    ]
    
    resultados = {}
    
    for character, ability in test_cases:
        resultado = test_habilidad_especifica(character, ability)
        resultados[f"{character}.{ability}"] = resultado
    
    print(f"\n📊 RESULTADOS FINALES:")
    exitos = sum(resultados.values())
    total = len(resultados)
    
    for test, resultado in resultados.items():
        status = "✅ ÉXITO" if resultado else "❌ FALLO"
        print(f"   {status}: {test}")
    
    print(f"\n🎯 ESTADÍSTICAS: {exitos}/{total} habilidades funcionan ({exitos/total*100:.1f}%)")
    
    return exitos == total

if __name__ == "__main__":
    success = test_todas_habilidades()
    if success:
        print("\n🎉 ¡TODAS LAS HABILIDADES FUNCIONAN CORRECTAMENTE!")
    else:
        print("\n🔧 Algunas habilidades necesitan ajustes (revisa los mensajes arriba)")