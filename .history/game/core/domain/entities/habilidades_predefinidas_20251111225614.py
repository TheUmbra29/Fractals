from .habilidad import Habilidad, TipoHabilidad

# ATAQUE BÁSICO - AMP (Simplificado)
AMP = Habilidad(
    id="amp",
    nombre="AMP",
    descripcion="Dispara un proyectil básico. Recupera 25 PH",
    tipo=TipoHabilidad.ATAQUE,
    costo_ph=0,
    td_e=0,
    rango=5,
    daño_base=6
)

# HABILIDAD ALPHA - Corte Fugaz (Simplificado)
CORTE_FUGAZ = Habilidad(
    id="corte_fugaz",
    nombre="Corte Fugaz", 
    descripcion="Un tajo rápido que inflige daño moderado",
    tipo=TipoHabilidad.ATAQUE,
    costo_ph=40,
    td_e=1,
    rango=1,
    daño_base=12
)

# HABILIDAD BETA - Destello Vácuo (Simplificado)
DESTELLO_VACUO = Habilidad(
    id="destello_vacuo",
    nombre="Destello Vácuo",
    descripcion="Teletransporte corto con daño en área pequeña",
    tipo=TipoHabilidad.ATAQUE,
    costo_ph=80,
    td_e=2,
    rango=3,
    area_efecto=1,
    daño_base=18
)

# HABILIDAD DEFINITIVA - Rayo del Vacío (MUY Simplificada)
RAYO_VACIO = Habilidad(
    id="rayo_vacio",
    nombre="Rayo del Vacío",
    descripcion="Proyectil de largo alcance que atraviesa obstáculos",
    tipo=TipoHabilidad.ATAQUE,
    costo_ph=0,
    td_e=4,
    rango=8,
    daño_base=30
)

# Ejemplo de habilidades de otras clases (debes definirlas)
CURA_RAPIDA = Habilidad(
    id="cura_rapida",
    nombre="Cura Rápida",
    descripcion="Recupera HP rápidamente",
    tipo=TipoHabilidad.CURACION,
    costo_ph=20,
    td_e=1,
    curacion_base=15
)
ESCUDO_PROTECTOR = Habilidad(
    id="escudo_protector",
    nombre="Escudo Protector",
    descripcion="Otorga un escudo temporal",
    tipo=TipoHabilidad.BUFF,
    costo_ph=30,
    td_e=2,
    efectos={"escudo": 20}
)
DESESTABILIZAR = Habilidad(
    id="desestabilizar",
    nombre="Desestabilizar",
    descripcion="Reduce la defensa enemiga",
    tipo=TipoHabilidad.DEBUFF,
    costo_ph=25,
    td_e=2,
    efectos={"defensa": -5}
)

HABILIDADES_POR_CLASE = {
    "daño": [AMP, CORTE_FUGAZ, DESTELLO_VACUO, RAYO_VACIO],
    "apoyo": [CURA_RAPIDA, ESCUDO_PROTECTOR],
    "tactico": [DESESTABILIZAR]
}
