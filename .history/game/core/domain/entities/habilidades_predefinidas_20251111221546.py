from .habilidad import Habilidad, TipoHabilidad

# Diccionario de habilidades por clase
HABILIDADES_POR_CLASE = {
    "guerrero": [
        Habilidad(
            id="atk_basic",
            nombre="Ataque Básico",
            descripcion="Golpea al enemigo con fuerza",
            tipo=TipoHabilidad.ATAQUE,
            costo_ph=0,
            td_e=0,
            rango=1,
            daño_base=12
        ),
        Habilidad(
            id="curar",
            nombre="Curación",
            descripcion="Recupera HP propio o aliado",
            tipo=TipoHabilidad.CURACION,
            costo_ph=10,
            td_e=1,
            curacion_base=18
        ),
    ],
    "mago": [
        Habilidad(
            id="fireball",
            nombre="Bola de Fuego",
            descripcion="Ataque mágico a distancia",
            tipo=TipoHabilidad.ATAQUE,
            costo_ph=15,
            td_e=2,
            rango=3,
            daño_base=22
        ),
        Habilidad(
            id="buff_mana",
            nombre="Aumentar Maná",
            descripcion="Buff temporal de PH",
            tipo=TipoHabilidad.BUFF,
            costo_ph=8,
            td_e=2,
            efectos={"ph": +10}
        ),
    ],
    # ...agrega más clases y habilidades según tu diseño
}
