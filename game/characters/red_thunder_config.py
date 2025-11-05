# CONFIGURACIONES DE RED THUNDER

RED_THUNDER_ABILITIES = {
    "basic_attack": {
        "name": "Disparo relámpago",
        "cost_ph": 0,
        "cooldown": 0,
        "range": 100,  # 🎯 ILIMITADO
        "selection_mode": "enemy",
        "effects": [
            {
                "type": "damage",
                "multiplier": 0.2,
                "damage_type": "energy"
            },
            {
                "type": "resource_recovery",
                "ph_recovery": 25
            }
        ]
    },
    
    "carrera_relampago": {
        "name": "Carrera Relámpago",
        "cost_ph": 40,
        "cooldown": 2,
        "range": 10,
        "selection_mode": "line",
        "effects": [
            {
                "type": "movement",  # 🎯 CAMBIADO: de damage a movement
                "move_type": "line_movement",  # 🎯 NUEVO TIPO
                "range": 10
            },
            {
                "type": "damage",  # 🎯 DAÑO ADICIONAL si hay enemigos
                "multiplier": 0.4,
                "damage_type": "physical",
                "target": "enemies"  # Solo daña enemigos
            },
            {
                "type": "status",
                "status_type": "Quemadura Cinética", 
                "duration": 2,
                "value": 0.15,
                "target": "enemies"  # Solo aplica a enemigos
            }
        ]
    },
    
    "red_thunderblast": {
        "name": "Red Thunderblast",
        "cost_ph": 60,
        "cooldown": 3,
        "range": 2,
        "selection_mode": "aoe",
        "effects": [
            {
                "type": "damage",
                "multiplier": 0.7,
                "aoe_radius": 2,
                "damage_type": "energy"
            },
            {
                "type": "buff",
                "stat_buffs": {"speed": 0.6},
                "duration": 2,
                "target": "self"
            }
        ]
    },
    
    "red_storm": {
        "name": "Tormenta Rojiza", 
        "cost_ph": 0,
        "energy_cost": 115,
        "cooldown": 4,
        "is_ultimate": True,
        "selection_mode": "self",
        "effects": [
            {
                "type": "buff",
                "stat_buffs": {"speed": 5.0, "attack": 1.0},
                "duration": 4,
                "target": "self"
            }
        ]
    }
}

RED_THUNDER_STATS = {
    'max_hp': 90,
    'current_hp': 90, 
    'max_ph': 100,
    'current_ph': 100,
    'attack': 90,
    'defense': 30,
    'speed': 18,
    'max_energy': 115
}

# 🎯 NUEVO: AÑADIR ESTAS LÍNEAS QUE FALTABAN
RED_THUNDER_ENERGY_SOURCES = {
    'on_hit': {'base': 12, 'type': 'flat'},
    'on_take_damage': {'base': 3, 'type': 'flat'},  
    'on_ability_use': {'base': 8, 'type': 'flat'},
    'on_kill': {'base': 20, 'type': 'flat'},
    'on_heal': {'base': 5, 'type': 'flat'},
    'on_buff': {'base': 6, 'type': 'flat'},
    'per_turn': {'base': 10, 'type': 'flat'}
}

RED_THUNDER_ENERGY_MULTIPLIERS = {
    'physical_damage': 1.5,
    'energy_damage': 1.0,
    'void_damage': 1.0,
    'light_damage': 1.0,
    'storm_damage': 1.8,
    'ultimate_ability': 0.0
}