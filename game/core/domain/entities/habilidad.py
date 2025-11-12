from enum import Enum
from typing import Optional, Dict, Any

class TipoHabilidad(Enum):
    ATAQUE = "ataque"
    CURACION = "curacion" 
    BUFF = "buff"
    DEBUFF = "debuff"
    MOVIMIENTO = "movimiento"

class Habilidad:
    def __init__(self, 
                 id: str,
                 nombre: str, 
                 descripcion: str,
                 tipo: TipoHabilidad,
                 costo_ph: int,
                 td_e: int,
                 rango: int = 1,
                 area_efecto: int = 0,
                 daño_base: int = 0,
                 curacion_base: int = 0,
                 efectos: Optional[Dict[str, Any]] = None):
        
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo
        self.costo_ph = costo_ph
        self.td_e_max = td_e
        self.td_e_actual = 0
        self.rango = rango
        self.area_efecto = area_efecto
        self.daño_base = daño_base
        self.curacion_base = curacion_base
        self.efectos = efectos or {}
    
    def puede_usar(self, usuario) -> bool:
        """Verifica si la habilidad puede ser usada"""
        return (usuario.stats.current_ph >= self.costo_ph and 
                self.td_e_actual == 0)
    
    def usar(self, usuario, objetivo=None, battle=None) -> str:
        """Ejecuta la habilidad y retorna mensaje de resultado"""
        if not self.puede_usar(usuario):
            return f"❌ No se puede usar {self.nombre}. PH insuficiente o en enfriamiento."
        
        # Consumir PH
        usuario.stats.current_ph -= self.costo_ph
        self.td_e_actual = self.td_e_max
        
        # Aplicar efecto según tipo
        if self.tipo == TipoHabilidad.ATAQUE and objetivo:
            return self._aplicar_ataque(usuario, objetivo, battle)
        elif self.tipo == TipoHabilidad.CURACION:
            return self._aplicar_curacion(usuario, objetivo)
        elif self.tipo == TipoHabilidad.BUFF:
            return self._aplicar_buff(usuario, objetivo)
        
        return f"✅ {usuario.name} usa {self.nombre}"
    
    def _aplicar_ataque(self, usuario, objetivo, battle) -> str:
        """Aplica daño considerando cobertura"""
        # Calcular probabilidad de impacto con cobertura
        hit_prob = battle.cover_system.get_hit_probability(
            usuario.position, objetivo.position
        )
        
        import random
        if random.random() <= hit_prob:
            daño = max(1, self.daño_base - objetivo.stats.defense)
            objetivo.stats.current_hp -= daño
            
            cover_status = battle.cover_system.get_cover_status(
                usuario.position, objetivo.position
            )
            
            if cover_status.value == "half":
                return f"✅ {usuario.name} usa {self.nombre} - {daño} daño (parcialmente bloqueado)"
            else:
                return f"✅ {usuario.name} usa {self.nombre} - {daño} daño"
        else:
            return f"❌ {self.nombre} falló - ¡Cobertura total!"
    
    def _aplicar_curacion(self, usuario, objetivo) -> str:
        """Aplica curación"""
        objetivo_real = objetivo or usuario
        curacion = min(self.curacion_base, 
                      objetivo_real.stats.max_hp - objetivo_real.stats.current_hp)
        objetivo_real.stats.current_hp += curacion
        
        if objetivo_real == usuario:
            return f"✨ {usuario.name} usa {self.nombre} - +{curacion} HP"
        else:
            return f"✨ {usuario.name} cura a {objetivo_real.name} - +{curacion} HP"
    
    def _aplicar_buff(self, usuario, objetivo) -> str:
        """Aplica buff temporal (simplificado)"""
        # Por ahora solo mensaje, luego implementamos efectos temporales
        objetivo_real = objetivo or usuario
        return f"🛡️ {usuario.name} da buff a {objetivo_real.name} con {self.nombre}"
    
    def reducir_cooldown(self):
        """Reduce el cooldown en 1 turno"""
        if self.td_e_actual > 0:
            self.td_e_actual -= 1
    
    def __str__(self):
        estado = "✅ Lista" if self.td_e_actual == 0 else f"🔄 TdE: {self.td_e_actual}"
        return f"{self.nombre} (PH: {self.costo_ph}) - {estado}"
