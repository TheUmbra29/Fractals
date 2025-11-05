# debug_imports_detailed.py
import sys
sys.path.append('.')

print("🔍 DIAGNÓSTICO DETALLADO DE IMPORTS...")

# Verificar ability_factory línea por línea
try:
    with open('game/systems/ability_factory.py', 'r') as f:
        lines = f.readlines()
        print("📄 Primeras 10 líneas de ability_factory.py:")
        for i, line in enumerate(lines[:10], 1):
            print(f"  {i}: {line.strip()}")
            
        # Buscar import problemático
        for i, line in enumerate(lines, 1):
            if "from game.systems.effect_system import" in line:
                print(f"❌ LÍNEA {i} PROBLEMÁTICA: {line.strip()}")
                
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")

# Verificar imports
try:
    from game.systems.ability_factory import AbilityFactory
    print("✅ AbilityFactory importa correctamente")
except Exception as e:
    print(f"❌ Error importando AbilityFactory: {e}")