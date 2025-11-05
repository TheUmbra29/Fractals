# game/characters/zoe_config.py
ZOE_STATS = {
    'max_hp': 100,
    'current_hp': 100, 
    'max_ph': 150,
    'current_ph': 150,
    'attack': 80,
    'defense': 40,
    'speed': 11,  # 1.1 * 10 para el sistema
    'max_energy': 120
}

ZOE_ENERGY_SOURCES = {
    'on_hit': {'base': 8, 'type': 'flat'},
    'on_take_damage': {'base': 5, 'type': 'flat'},  
    'on_ability_use': {'base': 10, 'type': 'flat'},
    'on_kill': {'base': 20, 'type': 'flat'},
    'per_turn': {'base': 6, 'type': 'flat'},
    'on_light_ability': {'base': 12, 'type': 'flat'},
    'on_ally_attack': {'base': 10, 'type': 'flat'}  # Para la pasiva
}

ZOE_ENERGY_MULTIPLIERS = {
    'physical_damage': 1.0,
    'energy_damage': 1.1,
    'void_damage': 1.0,
    'light_damage': 1.5,
    'storm_damage': 1.0,
    'healing': 1.3
}

ZOE_ABILITIES = {
    "basic_attack": {
        "name": "Toque de Luz",
        "cost_ph": 0,
        "cooldown": 0,
        "range": 3,
        "selection_mode": "enemy", 
        "effects": [
            {
                "type": "damage",
                "multiplier": 0.3,
                "damage_type": "light"
            },
            {
                "type": "resource_recovery",
                "ph_recovery": 25
            }
        ]
    },
    
    "torbellino_fe": {
        "name": "Torbellino de Fe",
        "cost_ph": 40,
        "cooldown": 2,
        "range": 4,
        "selection_mode": "position",
        "effects": [
            {
                "type": "heal",
                "value": 50,
                "calculation": {
                    "formula": "percentage_of_source_stat",
                    "stat": "attack",
                    "multiplier": 0.5
                },
                "target": "allies",
                "aoe_radius": 2
            },
            {
                "type": "apply_effect",
                "effect_id": "speed_buff", 
                "target": "allies",
                "aoe_radius": 2
            },
            {
                "type": "apply_effect",
                "effect_id": "speed_debuff",
                "target": "enemies",  
                "aoe_radius": 2
            }
        ]
    },
    
    "grito_tempestad": {
        "name": "Grito de Tempestad", 
        "cost_ph": 50,
        "cooldown": 4,
        "range": "global",
        "selection_mode": "global_ally",
        "effects": [
            {
                "type": "apply_effect",
                "effect_id": "comradeship",
                "target": "selected"
            }
        ]
    },
    
    "dawn_cataclysm": {
        "name": "Cataclismo del Alba",
        "cost_ph": 0,
        "energy_cost": 120, 
        "cooldown": 4,
        "is_ultimate": True,
        "selection_mode": "none",
        "effects": [
            {
                "type": "apply_effect",
                "effect_id": "synchronization", 
                "target": "all_allies"
            },
            {
                "type": "ultimate_recharge",
                "target": "all_allies",
                "value": 100
            }
        ]
    }
}