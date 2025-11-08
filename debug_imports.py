#!/usr/bin/env python3
"""
Prueba de integración del sistema de efectos
"""
import sys
import os
sys.path.append('.')

from game.core.logger import logger

def test_effects_system():
    """Prueba el sistema de efectos completo"""
    logger.info("🧪 Probando integración de efectos...")
    
    try:
        # Test 1: Crear sistema de efectos
        from game.systems.effect_system import EffectSystem
        effect_system = EffectSystem()
        
        # Test 2: Cargar configuración de efectos
        from game.data.effects import EFFECTS_CONFIG
        effect_system.load_effects_config(EFFECTS_CONFIG)
        
        # Test 3: Verificar efectos cargados
        stats = effect_system.get_effect_stats()
        logger.info(f"✅ Sistema de efectos cargado: {stats['effects_loaded']} efectos")
        
        # Test 4: Probar ApplyEffectComponent
        from game.systems.ability_factory import ApplyEffectComponent
        
        # Crear entidades de prueba
        class MockEntity:
            def __init__(self, name, team="player"):
                self.name = name
                self.team = team
                self.position = (0, 0)
                self.stats = {'current_hp': 100, 'max_hp': 100, 'speed': 10}
                self.battle_scene = None
        
        class MockCaster:
            def __init__(self):
                self.name = "TestCaster"
                self.team = "player"
                self.position = (0, 0)
                self.stats = {'current_hp': 100, 'max_hp': 100}
                self.battle_scene = type('MockScene', (), {'get_effect_system': lambda: effect_system})()
        
        # Crear contexto de prueba
        from game.core.action_base import ActionContext
        caster = MockCaster()
        target = MockEntity("TestTarget", "enemy")
        
        context = ActionContext(
            caster=caster,
            target=target,
            entities=[target]
        )
        context.extra_data = {'effect_system': effect_system}
        
        # Probar aplicación de efecto
        apply_component = ApplyEffectComponent({'effect_id': 'kinetic_burn', 'target': 'enemy'})
        success = apply_component.apply(context)
        
        if success:
            logger.info("✅ ApplyEffectComponent aplicó efecto correctamente")
            
            # Verificar que el efecto se aplicó
            effects = effect_system.get_entity_effects(target)
            logger.info(f"✅ Efectos en objetivo: {len(effects)}")
            
            for effect in effects:
                logger.info(f"   - {effect.name} (duración: {effect.duration})")
        else:
            logger.error("❌ ApplyEffectComponent falló")
        
        return success
        
    except Exception as e:
        logger.error("❌ Error en prueba de efectos", exception=e)
        return False

def test_effect_triggers():
    """Prueba que los efectos se activen correctamente"""
    try:
        from game.systems.effect_system import EffectSystem, GenericEffect
        
        # Crear efecto de prueba
        effect_config = {
            'id': 'test_effect',
            'name': 'Efecto de Prueba',
            'type': 'buff',
            'duration': 2,
            'actions': {
                'on_apply': [
                    {
                        'type': 'modify_stat',
                        'stat': 'speed',
                        'value': 10,
                        'operation': 'add'
                    }
                ]
            }
        }
        
        class MockEntity:
            def __init__(self):
                self.name = "TestEntity"
                self.stats = {'speed': 5}
        
        entity = MockEntity()
        source = MockEntity()
        source.name = "SourceEntity"
        
        effect = GenericEffect(effect_config, source)
        effect.on_apply(entity)
        
        logger.info(f"✅ Efecto aplicado. Velocidad: {entity.stats['speed']}")
        return entity.stats['speed'] == 15  # 5 + 10
        
    except Exception as e:
        logger.error("❌ Error en prueba de triggers", exception=e)
        return False

if __name__ == "__main__":
    success1 = test_effects_system()
    success2 = test_effect_triggers()
    
    if success1 and success2:
        logger.info("🎉 ¡Sistema de efectos completamente integrado!")
    else:
        logger.error("💥 Hay problemas con la integración de efectos")