# game/characters/red_thunder_config.py
RED_THUNDER_STATS = {
    'max_hp': 90,
    'current_hp': 90, 
    'max_ph': 100,
    'current_ph': 100,
    'attack': 90,
    'defense': 30,
    'speed': 18,  # 1.8 * 10 para el sistema
    'max_energy': 100
}

RED_THUNDER_ENERGY_SOURCES = {
    'on_hit': {'base': 12, 'type': 'flat'},
    'on_take_damage': {'base': 6, 'type': 'flat'},  
    'on_ability_use': {'base': 15, 'type': 'flat'},
    'on_kill': {'base': 25, 'type': 'flat'},
    'per_turn': {'base': 8, 'type': 'flat'},
    'on_storm_ability': {'base': 20, 'type': 'flat'}
}

RED_THUNDER_ENERGY_MULTIPLIERS = {
    'physical_damage': 1.0,
    'energy_damage': 1.3,
    'kinetic_damage': 1.8,
    'void_damage': 1.0,
    'light_damage': 1.0,
    'storm_damage': 2.0
}

RED_THUNDER_ABILITIES = {
    "basic_attack": {
        "name": "Disparo Relámpago",
        "cost_ph": 0,
        "cooldown": 0,
        "range": "infinite",
        "selection_mode": "enemy",
        "effects": [
            {
                "type": "damage",
                "multiplier": 0.2,
                "damage_type": "energy",
                "calculation": {
                    "formula": "scales_with_source_stat",
                    "stat": "speed",
                    "multiplier": 1.0
                }
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
                "type": "damage",
                "multiplier": 0.4,
                "damage_type": "kinetic", 
                "calculation": {
                    "formula": "scales_with_source_stat",
                    "stat": "speed", 
                    "multiplier": 1.0
                }
            },
            {
                "type": "apply_effect",
                "effect_id": "kinetic_burn",
                "target": "enemy"
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
                "damage_type": "kinetic",
                "calculation": {
                    "formula": "scales_with_source_stat", 
                    "stat": "speed",
                    "multiplier": 1.0
                }
            },
            {
                "type": "apply_effect",
                "effect_id": "overload", 
                "target": "self"
            }
        ]
    },
    
    "red_storm": {
        "name": "Tormenta Rojiza", 
        "cost_ph": 0,
        "energy_cost": 100,
        "cooldown": 4,
        "is_ultimate": True,
        "selection_mode": "none",
        "effects": [
            {
                "type": "apply_effect",
                "effect_id": "hyper_speed",
                "target": "self"
            },
            {
                "type": "apply_effect", 
                "effect_id": "improved_dash",
                "target": "self"
            }
        ]
    }
}