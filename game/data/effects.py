# game/data/effects.py
"""
CONFIGURACIÓN DE TODOS LOS EFECTOS - DATA-DRIVEN
"""

EFFECTS_CONFIG = {
    # RED THUNDER
    "kinetic_burn": {
        "id": "kinetic_burn",
        "name": "Quemadura Cinética", 
        "type": "debuff",
        "duration": 2,
        "actions": {
            "on_turn_start": [
                {
                    "type": "damage",
                    "value": 15,
                    "damage_type": "kinetic",
                    "calculation": {
                        "formula": "scales_with_source_stat", 
                        "stat": "speed",
                        "multiplier": 1.0
                    }
                }
            ]
        }
    },
    
    "overload": {
        "id": "overload",
        "name": "Sobrecarga Cinética",
        "type": "buff", 
        "duration": 2,
        "actions": {
            "on_apply": [
                {
                    "type": "modify_stat",
                    "stat": "speed", 
                    "value": 0.6,
                    "operation": "multiply"
                }
            ],
            "on_remove": [
                {
                    "type": "modify_stat", 
                    "stat": "speed",
                    "value": 0,
                    "operation": "set"  
                }
            ]
        }
    },
    
    # ZOE
    "comradeship": {
        "id": "comradeship",
        "name": "Camaradería",
        "type": "buff",
        "duration": 3,
        "actions": {
            "on_apply": [
                {
                    "type": "modify_stat",
                    "stat": "attack",
                    "value": 0.5,
                    "operation": "multiply"
                },
                {
                    "type": "modify_stat", 
                    "stat": "defense",
                    "value": 60,
                    "operation": "add"
                }
            ],
            "on_damage_taken": [
                {
                    "type": "modify_damage",
                    "modifier_type": "incoming", 
                    "operation": "reduce_percent",
                    "value": 0.3
                }
            ]
        }
    },
    
    "speed_buff": {
        "id": "speed_buff", 
        "name": "Aumento de Velocidad",
        "type": "buff",
        "duration": 2,
        "actions": {
            "on_apply": [
                {
                    "type": "modify_stat",
                    "stat": "speed",
                    "value": 0.25,
                    "operation": "multiply" 
                }
            ]
        }
    },
    
    "speed_debuff": {
        "id": "speed_debuff",
        "name": "Reducción de Velocidad", 
        "type": "debuff",
        "duration": 1,
        "actions": {
            "on_apply": [
                {
                    "type": "modify_stat",
                    "stat": "speed",
                    "value": -0.3,
                    "operation": "multiply"
                }
            ]
        }
    },

        "hyper_speed": {
        "id": "hyper_speed",
        "name": "Hipervelocidad",
        "type": "buff", 
        "duration": 999,
        "actions": {
            "on_apply": [
                {
                    "type": "modify_stat",
                    "stat": "speed", 
                    "value": 5.0,
                    "operation": "add"
                }
            ]
        }
    },

    "improved_dash": {
        "id": "improved_dash", 
        "name": "Embestida Mejorada",
        "type": "buff",
        "duration": 999,
        "actions": {
            "on_apply": [
                {
                    "type": "custom",
                    "callback": "enable_improved_dash"
                }
            ]
        }
    },

    "ultimate_recharge": {
        "id": "ultimate_recharge", 
        "name": "Recarga Definitiva",
        "type": "buff",
        "duration": 0,
        "actions": {
            "on_apply": [
                {
                    "type": "custom",
                    "callback": "recharge_ultimate"
                }
            ]
        }
    }
}