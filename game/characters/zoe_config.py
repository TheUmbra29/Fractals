# CONFIGURACIONES DE ZOE

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
            }
        ]
    },
    
    "torbellino_fe": {
        "name": "Torbellino de fé",
        "cost_ph": 40,
        "cooldown": 2,
        "range": 5,
        "selection_mode": "position",
        "effects": [
            {
                "type": "heal",
                "amount": 40,
                "aoe_radius": 2,
                "target": "allies"
            },
            {
                "type": "buff",
                "stat_buffs": {"speed": 0.25},
                "duration": 2,
                "aoe_radius": 2,
                "target": "allies"
            },
            {
                "type": "damage",
                "multiplier": 0.1,
                "aoe_radius": 2,
                "damage_type": "light",
                "target": "enemies"
            }
        ]
    },
    
    "grito_tempestad": {
        "name": "Grito de tempestad",
        "cost_ph": 50,
        "cooldown": 4,
        "range": 100,
        "selection_mode": "global_ally",
        "effects": [
            {
                "type": "buff",
                "name": "Camaradería",
                "stat_buffs": {"attack": 0.5, "defense": 60},
                "duration": 3,
                "target": "selected"
            }
        ]
    },
    
    "dawn_cataclysm": {
        "name": "Cataclismo del Alba",
        "cost_ph": 0, 
        "energy_cost": 150,
        "cooldown": 5,
        "is_ultimate": True,
        "selection_mode": "global_self",
        "effects": [
            {
                "type": "resource_recovery",
                "energy_recovery": 100,
                "target": "all_allies"
            },
            {
                "type": "buff",
                "name": "Sincronización", 
                "stat_buffs": {"defense": 30},
                "duration": 3,
                "target": "all_allies"
            },
            {
                "type": "heal",
                "amount": 50,
                "target": "all_allies"
            }
        ]
    }
}

ZOE_STATS = {
    'max_hp': 100,
    'current_hp': 100, 
    'max_ph': 150,
    'current_ph': 150,
    'attack': 80,
    'defense': 40,
    'speed': 11,
    'max_energy': 150
}

# 🎯 CONFIGURACIÓN DE ENERGÍA PARA ZOE
ZOE_ENERGY_SOURCES = {
    'on_hit': {'base': 5, 'type': 'flat'},
    'on_take_damage': {'base': 8, 'type': 'flat'},  
    'on_ability_use': {'base': 15, 'type': 'flat'},
    'on_kill': {'base': 15, 'type': 'flat'},
    'on_heal': {'base': 12, 'type': 'flat'},
    'on_buff': {'base': 15, 'type': 'flat'},
    'per_turn': {'base': 8, 'type': 'flat'}
}

ZOE_ENERGY_MULTIPLIERS = {
    'physical_damage': 0.8,
    'energy_damage': 1.0,
    'void_damage': 1.0,
    'light_damage': 1.5,
    'storm_damage': 1.0,
    'ultimate_ability': 0.0
}