#!/usr/bin/env python3
"""
SISTEMA DE DIAGNÓSTICO COMPLETO DE HABILIDADES
Testea todas las habilidades y detecta anomalías automáticamente
"""

import sys
import os
import traceback
sys.path.append('.')

class HabilidadTester:
    def __init__(self):
        self.resultados = {}
        self.errores_graves = []
        self.anomalias_detectadas = []
    
    def test_habilidad_individual(self, character_name, ability_key, config_esperada=None):
        """Test individual de una habilidad específica con verificación completa"""
        print(f"\n🔍 TESTEANDO {character_name} -> {ability_key}")
        
        try:
            from game.characters.character_registry import CharacterRegistry
            from game.core.action_base import ActionContext
            
            # Crear personaje
            character = CharacterRegistry.create_character(character_name, (0, 0))
            
            # Verificar que la habilidad existe
            if ability_key not in character.actions:
                error_msg = f"❌ Habilidad {ability_key} no encontrada en {character.name}"
                print(error_msg)
                self.errores_graves.append(error_msg)
                return False
            
            ability = character.actions[ability_key]
            print(f"✅ Habilidad encontrada: {ability.name}")
            
            # Verificaciones básicas
            info_habilidad = {
                'nombre': ability.name,
                'costo_ph': ability.cost_ph,
                'rango': ability.range,
                'modo_seleccion': ability.selection_mode,
                'cooldown': ability.cooldown,
                'tipo': ability.type
            }
            
            print(f"   - Costo PH: {ability.cost_ph}")
            print(f"   - Rango: {ability.range}")
            print(f"   - Modo selección: {ability.selection_mode}")
            print(f"   - Cooldown: {ability.cooldown}")
            
            # Verificar configuración esperada si se proporciona
            if config_esperada:
                self._verificar_configuracion(ability, config_esperada, character_name, ability_key)
            
            # Crear objetivos de prueba
            class MockEntity:
                def __init__(self, name="Target", team="enemy", position=(1,1), stats=None):
                    self.name = name
                    self.team = team
                    self.position = position
                    self.stats = stats or {
                        'max_hp': 100, 'current_hp': 100,
                        'max_ph': 50, 'current_ph': 50,
                        'attack': 10, 'defense': 5, 'speed': 5
                    }
                    self.has_moved = False
                    self.has_acted = False
                    self.actions = {}
                    self.energy_stats = {'current_energy': 0, 'max_energy': 100}
                
                def gain_energy(self, amount, source):
                    self.energy_stats['current_energy'] = min(
                        self.energy_stats['max_energy'], 
                        self.energy_stats['current_energy'] + amount
                    )
                
                def get_energy_absolute(self):
                    return self.energy_stats['current_energy']
                
                def can_use_ultimate(self, config):
                    return self.energy_stats['current_energy'] >= config.get('energy_cost', 100)
                
                def consume_ultimate_energy(self, cost):
                    if self.energy_stats['current_energy'] >= cost:
                        self.energy_stats['current_energy'] -= cost
                        return True
                    return False
            
            # Configurar contexto según el modo de selección
            context = self._crear_contexto_prueba(ability, character, MockEntity)
            
            # Verificar si puede ejecutarse
            can_execute = ability.can_execute(context)
            print(f"   - Puede ejecutarse: {can_execute}")
            
            if not can_execute:
                # Diagnosticar por qué no puede ejecutarse
                self._diagnosticar_bloqueo(ability, context, character)
                return False
            
            # Estado antes de ejecución
            estado_antes = self._capturar_estado(context)
            
            # Ejecutar habilidad
            success = ability.execute(context)
            print(f"   - Éxito ejecución: {success}")
            
            if success:
                # Estado después de ejecución
                estado_despues = self._capturar_estado(context)
                
                # Analizar cambios
                self._analizar_cambios(estado_antes, estado_despues, ability, context)
                
                # Verificar efectos secundarios
                self._verificar_efectos_secundarios(ability, context, character)
                
                print(f"   ✅ {ability_key} FUNCIONA CORRECTAMENTE")
                return True
            else:
                print(f"   ❌ La ejecución de {ability_key} falló")
                self.anomalias_detectadas.append(f"{character_name}.{ability_key}: Ejecución falló")
                return False
            
        except Exception as e:
            error_msg = f"❌ ERROR CRÍTICO testeando {ability_key}: {e}"
            print(error_msg)
            traceback.print_exc()
            self.errores_graves.append(error_msg)
            return False
    
    def _crear_contexto_prueba(self, ability, character, MockEntity):
        """Crea el contexto de prueba según el modo de selección"""
        from game.core.action_base import ActionContext
        
        if ability.selection_mode == "enemy":
            target = MockEntity("Enemigo", "enemy", (1, 0))
            context = ActionContext(caster=character, target=target, entities=[character, target])
        
        elif ability.selection_mode == "chain":
            targets = [
                MockEntity("Enemigo1", "enemy", (1, 0)),
                MockEntity("Enemigo2", "enemy", (2, 0)),
                MockEntity("Enemigo3", "enemy", (3, 0))
            ]
            context = ActionContext(caster=character, entities=targets)
        
        elif ability.selection_mode == "position":
            context = ActionContext(caster=character, target_position=(3, 3), entities=[character])
        
        elif ability.selection_mode == "line":
            context = ActionContext(caster=character, entities=[])
            context.extra_data = {'direction': (1, 0), 'line_length': 3}
        
        elif ability.selection_mode == "aoe":
            targets = [
                MockEntity("Enemigo1", "enemy", (1, 0)),
                MockEntity("Enemigo2", "enemy", (1, 1)),
            ]
            context = ActionContext(caster=character, entities=targets)
        
        elif ability.selection_mode == "self":
            context = ActionContext(caster=character, target=character, entities=[character])
        
        elif ability.selection_mode == "ally":
            aliado = MockEntity("Aliado", "player", (0, 1))
            context = ActionContext(caster=character, target=aliado, entities=[character, aliado])
        
        else:  # none, global_self, etc.
            context = ActionContext(caster=character, entities=[character])
        
        return context
    
    def _capturar_estado(self, context):
        """Captura el estado actual del contexto"""
        estado = {
            'hp_caster': context.caster.stats['current_hp'],
            'ph_caster': context.caster.stats['current_ph'],
            'energia_caster': getattr(context.caster, 'energy_stats', {}).get('current_energy', 0),
            'has_acted': context.caster.has_acted,
            'has_moved': context.caster.has_moved
        }
        
        # Capturar estado de objetivos
        if context.target:
            estado['hp_target'] = context.target.stats['current_hp']
        
        if context.entities:
            estado['hp_entidades'] = [e.stats['current_hp'] for e in context.entities]
        
        return estado
    
    def _analizar_cambios(self, estado_antes, estado_despues, ability, context):
        """Analiza los cambios producidos por la habilidad"""
        print("   📊 ANÁLISIS DE CAMBIOS:")
        
        # PH del caster
        ph_antes = estado_antes['ph_caster']
        ph_despues = estado_despues['ph_caster']
        costo_real = ph_antes - ph_despues
        print(f"   - PH: {ph_antes} -> {ph_despues} (costo real: {costo_real}, esperado: {ability.cost_ph})")
        
        if costo_real != ability.cost_ph:
            self.anomalias_detectadas.append(
                f"Costo PH incorrecto: real={costo_real}, esperado={ability.cost_ph}"
            )
        
        # HP de objetivos
        if 'hp_target' in estado_antes and context.target:
            hp_antes = estado_antes['hp_target']
            hp_despues = estado_despues.get('hp_target', hp_antes)
            danio = hp_antes - hp_despues
            if danio > 0:
                print(f"   - Daño a objetivo: {danio} HP")
            elif danio < 0:
                print(f"   - Curación a objetivo: {-danio} HP")
        
        # HP de múltiples entidades
        if 'hp_entidades' in estado_antes and context.entities:
            hp_antes_lista = estado_antes['hp_entidades']
            hp_despues_lista = estado_despues.get('hp_entidades', hp_antes_lista)
            
            for i, (antes, despues) in enumerate(zip(hp_antes_lista, hp_despues_lista)):
                cambio = antes - despues
                if cambio != 0:
                    print(f"   - Entidad {i+1}: {cambio:+d} HP")
    
    def _diagnosticar_bloqueo(self, ability, context, character):
        """Diagnostica por qué una habilidad no puede ejecutarse"""
        print("   🔍 DIAGNÓSTICO DE BLOQUEO:")
        
        # PH insuficiente
        if character.stats['current_ph'] < ability.cost_ph:
            print(f"   - ❌ PH insuficiente: {character.stats['current_ph']}/{ability.cost_ph}")
        
        # Cooldown activo
        if ability.current_cooldown > 0:
            print(f"   - ❌ En cooldown: {ability.current_cooldown} turnos restantes")
        
        # Ya actuó este turno
        if ability.type == 'ability' and character.has_acted:
            print("   - ❌ Ya actuó este turno")
        
        # Ya se movió este turno
        if ability.type == 'movement' and character.has_moved:
            print("   - ❌ Ya se movió este turno")
        
        # Energía insuficiente para ultimate
        if hasattr(ability, 'is_ultimate') and ability.is_ultimate:
            if not character.can_use_ultimate(ability.ability_config):
                energia_actual = character.get_energy_absolute()
                costo_energia = ability.energy_cost
                print(f"   - ❌ Energía insuficiente para ultimate: {energia_actual}/{costo_energia}")
    
    def _verificar_configuracion(self, ability, config_esperada, character_name, ability_key):
        """Verifica que la configuración de la habilidad coincida con lo esperado"""
        print("   ⚙️  VERIFICANDO CONFIGURACIÓN:")
        
        for clave, valor_esperado in config_esperada.items():
            valor_real = getattr(ability, clave, None)
            if valor_real != valor_esperado:
                print(f"   - ❌ {clave}: esperado={valor_esperado}, real={valor_real}")
                self.anomalias_detectadas.append(
                    f"{character_name}.{ability_key}.{clave}: esperado={valor_esperado}, real={valor_real}"
                )
            else:
                print(f"   - ✅ {clave}: {valor_real}")
    
    def _verificar_efectos_secundarios(self, ability, context, character):
        """Verifica efectos secundarios como cambios de estado"""
        print("   🔄 VERIFICANDO EFECTOS SECUNDARIOS:")
        
        # Verificar si el caster ya actuó
        if character.has_acted:
            print("   - ✅ Caster marcado como 'ya actuó'")
        else:
            print("   - ❌ Caster NO marcado como 'ya actuó' (posible bug)")
            self.anomalias_detectadas.append(f"{ability.name}: Caster no marcado como has_acted")
        
        # Verificar movimiento pendiente
        if hasattr(character, 'pending_post_action_move') and character.pending_post_action_move:
            print(f"   - ✅ Movimiento posterior preparado: {character.post_action_move_range} casillas")
        
        # Verificar cambios de posición
        if hasattr(context, 'target_position') and context.target_position:
            if character.position != (0, 0):  # Posición inicial
                print(f"   - ✅ Cambio de posición: {character.position}")
    
    def test_todas_habilidades_personaje(self, character_name):
        """Testea todas las habilidades de un personaje"""
        print(f"\n🎯 TESTEANDO TODAS LAS HABILIDADES DE {character_name.upper()}")
        
        try:
            from game.characters.character_registry import CharacterRegistry
            
            # Crear personaje
            character = CharacterRegistry.create_character(character_name, (0, 0))
            
            habilidades = list(character.actions.keys())
            print(f"📋 Habilidades encontradas: {habilidades}")
            
            resultados_personaje = {}
            for ability_key in habilidades:
                if ability_key == "move":  # Saltar movimiento básico
                    continue
                
                resultado = self.test_habilidad_individual(character_name, ability_key)
                resultados_personaje[ability_key] = resultado
            
            self.resultados[character_name] = resultados_personaje
            
        except Exception as e:
            error_msg = f"❌ ERROR testeando personaje {character_name}: {e}"
            print(error_msg)
            self.errores_graves.append(error_msg)
    
    def test_todos_personajes(self):
        """Testea todos los personajes y sus habilidades"""
        print("🎮 INICIANDO DIAGNÓSTICO COMPLETO DEL SISTEMA DE HABILIDADES")
        
        personajes = ["ricchard", "red_thunder", "zoe"]
        
        for personaje in personajes:
            self.test_todas_habilidades_personaje(personaje)
    
    def generar_reporte(self):
        """Genera un reporte completo del diagnóstico"""
        print("\n" + "="*60)
        print("📊 REPORTE FINAL DE DIAGNÓSTICO")
        print("="*60)
        
        # Estadísticas generales
        total_habilidades = sum(len(habs) for habs in self.resultados.values())
        habilidades_exitosas = sum(sum(resultados.values()) for resultados in self.resultados.values())
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   - Personajes testeados: {len(self.resultados)}")
        print(f"   - Habilidades testeadas: {total_habilidades}")
        print(f"   - Habilidades exitosas: {habilidades_exitosas}")
        print(f"   - Tasa de éxito: {(habilidades_exitosas/total_habilidades*100 if total_habilidades > 0 else 0):.1f}%")
        
        # Resultados por personaje
        print(f"\n🎭 RESULTADOS POR PERSONAJE:")
        for personaje, resultados in self.resultados.items():
            exitos = sum(resultados.values())
            total = len(resultados)
            porcentaje = (exitos/total*100) if total > 0 else 0
            print(f"   - {personaje}: {exitos}/{total} ({porcentaje:.1f}%)")
            
            for habilidad, resultado in resultados.items():
                estado = "✅" if resultado else "❌"
                print(f"     {estado} {habilidad}")
        
        # Anomalías detectadas
        if self.anomalias_detectadas:
            print(f"\n⚠️  ANOMALÍAS DETECTADAS ({len(self.anomalias_detectadas)}):")
            for anomalia in self.anomalias_detectadas:
                print(f"   - {anomalia}")
        
        # Errores graves
        if self.errores_graves:
            print(f"\n🚨 ERRORES GRAVES ({len(self.errores_graves)}):")
            for error in self.errores_graves:
                print(f"   - {error}")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if not self.errores_graves and not self.anomalias_detectadas:
            print("   - ✅ ¡Sistema de habilidades funcionando perfectamente!")
        else:
            if self.errores_graves:
                print("   - 🔧 Revisar errores graves antes de continuar")
            if self.anomalias_detectadas:
                print("   - ⚠️  Investigar anomalías detectadas")
        
        print("="*60)
        
        return len(self.errores_graves) == 0

def test_habilidad_especifica_detallada(character_name, ability_key):
    """Función para test detallado de una habilidad específica"""
    tester = HabilidadTester()
    resultado = tester.test_habilidad_individual(character_name, ability_key)
    
    if resultado:
        print(f"\n🎉 {character_name}.{ability_key} - TEST EXITOSO")
    else:
        print(f"\n💥 {character_name}.{ability_key} - TEST FALLIDO")
    
    return resultado

def diagnostico_completo():
    """Ejecuta el diagnóstico completo del sistema"""
    tester = HabilidadTester()
    tester.test_todos_personajes()
    return tester.generar_reporte()

if __name__ == "__main__":
    print("🔧 SISTEMA DE DIAGNÓSTICO DE HABILIDADES")
    print("Opción 1: Diagnóstico completo")
    print("Opción 2: Test de habilidad específica")
    
    opcion = input("Selecciona opción (1/2): ").strip()
    
    if opcion == "1":
        print("\n🚀 INICIANDO DIAGNÓSTICO COMPLETO...")
        exito = diagnostico_completo()
        sys.exit(0 if exito else 1)
    
    elif opcion == "2":
        personaje = input("Personaje (ricchard/red_thunder/zoe): ").strip()
        habilidad = input("Habilidad (ej: corte_fugaz, carrera_relampago): ").strip()
        
        if personaje and habilidad:
            test_habilidad_especifica_detallada(personaje, habilidad)
        else:
            print("❌ Debes especificar personaje y habilidad")
    
    else:
        print("❌ Opción no válida")