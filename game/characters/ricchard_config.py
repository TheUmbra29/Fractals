RICCHARD_STATS = {
    'max_hp': 100,
    'current_hp': 100, 
    'max_ph': 130,
    'current_ph': 130,
    'attack': 100,
    'defense': 40,
    'speed': 20,
    'max_energy': 120
}

RICCHARD_ABILITIES = {
    "basic_attack": {
        "name": "AMP",
        "cost_ph": 0,
        "cooldown": 0,
        "range": 10,
        "selection_mode": "enemy",
        "effects": [
            {
                "type": "damage",
                "multiplier": 0.4,
                "damage_type": "energy"
            },
            {
                "type": "resource_recovery",
                "ph_recovery": 25
            }
        ]
    },
    
    "corte_fugaz": {
        "name": "Corte Fugaz", 
        "cost_ph": 40,
        "cooldown": 1,
        "range": 6,
        "selection_mode": "chain",
        "min_targets": 1,
        "max_targets": 3,
        "effects": [
            {
                "type": "chain_movement",
                "multiplier": [0.5, 0.65, 0.9],
                "damage_type": "physical",
                "movement_pattern": "behind_last"
            }
        ]
    },
    
    "destello_vacuo": {
        "name": "Destello Vácuo",
        "cost_ph": 80, 
        "cooldown": 2,
        "range": 6,
        "selection_mode": "position",
        "effects": [
            {
                "type": "movement",
                "move_type": "teleport",
                "range": 6
            },
            {
                "type": "damage", 
                "multiplier": 1.4,
                "aoe_radius": 2,
                "damage_type": "void"
            }
        ]
    },
    
    "rayo_vacio": {
        "name": "Rayo del Vacío",
        "cost_ph": 0,
        "energy_cost": 120,
        "cooldown": 4, 
        "is_ultimate": True,
        "range": "10",
        "selection_mode": "line",
        "effects": [
            {
                "type": "damage",
                "multiplier": 2.5,
                "damage_type": "void",
                "pierce_through": True,
                "aoe_radius": 1,
                "range": "infinite"
            }
        ]
    }
}

RICCHARD_ENERGY_SOURCES = {
    'on_hit': {'base': 10, 'type': 'flat'},
    'on_take_damage': {'base': 8, 'type': 'flat'},  
    'on_ability_use': {'base': 12, 'type': 'flat'},
    'on_kill': {'base': 30, 'type': 'flat'},
    'per_turn': {'base': 8, 'type': 'flat'},
    'on_void_ability': {'base': 15, 'type': 'flat'}
}

RICCHARD_ENERGY_MULTIPLIERS = {
    'physical_damage': 1.0,
    'energy_damage': 1.2,
    'void_damage': 2.0,
    'light_damage': 1.0,
    'storm_damage': 1.0
}