import configs

def calculate_radiation_to_msv(value):
    return int(46861 * value)


def calculate_radiation_to_points(value):
    return round(value / 46861, 6)


def calculate_normal_to_int(value):
    return value * 1000


def calculate_int_to_normal(value):
    return value / 1000


def calculate_points_to_val(value, coeff):
    return int(coeff * value)


def calculate_val_to_points(value, coeff):
    return round(value / coeff, 6)


def update_armor_params():
    armor_keys = ['burn_protection', 'shock_protection', 'radiation_protection', 'chemical_burn_protection',
                  'telepatic_protection', 'fire_wound_protection', 'wound_protection', 'strike_protection',
                  'explosion_protection']
    max_keys = ["fire_zone_max_power", "electra_zone_max_power", "radio_zone_max_power", "acid_zone_max_power",
                "psi_zone_max_power", "max_fire_wound_protection", "max_wound_protection", "max_fire_wound_protection",
                "max_fire_wound_protection"]
    for armor_key, max_key in zip(armor_keys, max_keys):
        armor_params_coeffs[armor_key] = 1000 / configs.max_armor_values[max_key]


simple_categories = {"inv_weight": "Weight",
                     "cost": "Cost",
                     "additional_inventory_weight": "Carry weight increase",
                     "burn_protection": "Burn protection",
                     "shock_protection": "Shock protection",
                     "radiation_protection": "Radiation protection",
                     "chemical_burn_protection": "Chemical burn protection",
                     "telepatic_protection": "Telepathy protection",
                     "strike_protection": "Impact protection",
                     "explosion_protection": "Explosion protection",
                     "fire_wound_protection": "Bullet damage protection",
                     "wound_protection": "Rupture protection",
                     "power_loss": "Stamina recovery penalty",
                     "repair_type": "Repair type",
                     "community": "Belongs to",
                     "health_restore_speed": "Health restoration",
                     "satiety_restore_speed": "Satiety increse",
                     "power_restore_speed": "Stamina recovery",
                     "radiation_restore_speed": "Radiation",
                     "bleeding_restore_speed": "Bleeding stopping",
                     "burn_immunity": "Burn damage immunity",
                     "telepatic_immunity": "Telepathic damage immunity",
                     "strike_immunity": "Impact damage immunity",
                     "wound_immunity": "Rupture damage immunity",
                     "explosion_immunity": "Explosion damage immunity",
                     "chemical_burn_immunity": "Chemical burn damage immunity",
                     "shock_immunity": "Shock damage immunity",
                     "fire_wound_immunity": "Bullet damage immunity",
                     "radiation_immunity": "Radiation damage immunity",
                     "rpm": "Fire rate",
                     "fire_dispersion_base": "Weapon spread",
                     "fire_modes": "Fire modes",
                     "ammo_mag_size": "Mag size",
                     "silencer_name": "Matching silencer",
                     "fire_distance": "Weapon range",
                     "bullet_speed": "Bullet speed",
                     "hit_impulse": "Weapon hit stagger",
                     "hit_power": "Damage",
                     "repair_only": "Repairs",
                     "repair_min_condition": "Minimum repair condition",
                     "repair_add_condition": "Repair value",
                     "repair_part_bonus": "Bonus repair points",
                     # "use_condition": "Condition degradation",
                     "degradation_factor": "Condition degradation per use",
                     "disassemble_tool": "Can be used as disassemble tool",
                     "tier": "Item tier",
                     "artefact_count": "Artifact slots",
                     "repair_parts_sections": "Available parts",
                     "eat_satiety": "Satiety gain",
                     "eat_thirstiness": "Thirst increase",
                     "eat_radiation": "Radiation gain",
                     "eat_sleepiness": "Sleepiness gain",
                     "eat_health": "Health gain",
                     "eat_power": "Stamina gain",
                     "eat_alcohol": "Alcohol gain",
                     "wounds_heal_perc": "Wound healing",
                     "boost_time": "Effect time",
                     "boost_max_weight": "Max carry weight gain",
                     "boost_power_restore": "Stamina recovery gain",
                     "boost_health_restore": "Health recovery gain",
                     "boost_radiation_restore": "Radiation recovery gain",
                     "boost_bleeding_restore": "Bleed stopping",
                     "boost_radiation_protection": "Radiation protection",
                     "boost_telepat_protection": "Telepathy protection",
                     "boost_chemburn_protection": "Toxicity protection",
                     "k_disp": "Ammo dispersion factor",
                     "k_hit": "Hit damage modification factor",
                     "k_impulse": "Stagger impulse factor",
                     "k_ap": "Armor penetration factor",
                     # "k_disp": "Bullet spread",
                     "impair": "Weapon wear factor",
                     "sprint_allowed": "Sprint allowed",
                     "helmet_avaliable": "Allows to wear helmet",
                     "backpack_avaliable": "Allows to wear backpack",
                     "cooking_part": "Can be used for cooking",
                     "allow_repair": "Can be repaired",
                     "use_condition": "Can deteriorate",
                     "dont_stack": "Disallow stacking",
                     "remove_after_use": "Remove after use",
                     "can_trade": "Can be traded",
                     "default_to_ruck": "Move to backpack after picking up",
                     "ammo_class": "Type of ammo used",
                     # "silencer_name": "Matching silencer",
                     "bullet_hit_power_k": "Hit damage modification factor",
                     "bullet_hit_impulse_k": "Stagger impulse factor",
                     "bullet_speed_k": "Bullet speed factor",
                     "fire_dispersion_base_k": "Fire spread factor (more is worse)",
                     "buy_item_exponent": "Price modifier for trader selling",
                     "sell_item_exponent": "Price modifier for trader buying",
                     "Health": "Health",
                     "MinSpeed": "Minimal speed",
                     "MaxSpeed": "Maximal speed",
                     "going_speed": "Move speed",
                     "search_speed": "Speed when not triggered",
                     "smart_terrain_choose_interval": "Time lingering around single smart terrain",
                     "panic_threshold": "Panic threshold",
                     "SoundThreshold": "Sound detection threshold",
                     "eye_fov": "Field of view (degrees?)",
                     "eye_range": "Sight range",
                     "max_hear_distance": "Sound detection distance",
                     "MinAttackDist": "Minimum attack distance",
                     "MaxAttackDist": "Maximum attack distance",
                     "hit_type": "Damage type",
                     "max_item_mass": "Maximum carry weight",
                     "jump_speed": "Jump speed",
                     "crouch_coef": "Crouching speed factor",
                     "climb_coef": "Climbing speed factor",
                     "run_coef": "Running speed factor",
                     "sprint_coef": "Sprinting speed factor",
                     "run_back_coef": "Running backwards speed factor",
                     "walk_back_coef": "Walking backwards speed factor",
                     "sprint_strafe_coef": "Sprint strafing factor",
                     "pickup_info_radius": "Distance where items appear after pressing 'f'",
                     "feel_grenade_radius": "Grenade stagger radius",
                     "feel_grenade_time": "Grenade stagger time",
                     "hit_probability_gd_novice": "Hit probability (Novice)",
                     "hit_probability_gd_stalker": "Hit probability (Stalker)",
                     "hit_probability_gd_veteran": "Hit probability (Veteran)",
                     "hit_probability_gd_master": "Hit probability (Master)",
                     "satiety_v": "Rate of satiety reduction with time",
                     "radiation_v": "Radiation reduction rate",
                     "satiety_power_v": "Satiety stamina drop factor",
                     "satiety_health_v": "Satiety health drop factor",
                     "satiety_critical": "Critical satiety value (before health starts decreasing)",
                     "radiation_health_v": "Radiation health decrease factor",
                     "morale_v": "Morale recovery rate",
                     "psy_health_v": "Psy-health recovery rate",
                     "alcohol_v": "Alcohol level recovery rate",
                     "health_hit_part": "Damage to health loss ratio",
                     "power_hit_part": "Damage to stamina loss ratio",
                     "max_power_leak_speed": "Fatigue accumulation per second (lowers maximum stamina)",
                     "max_walk_weight": "Maximum carry weight before being unable to move",
                     "bleeding_v": "Blood loss at nominal wound per second",
                     "wound_incarnation_v": "Wound healing rate",
                     "min_wound_size": "Minimal wound size (smaller wounds are considered healed)",
                     "bleed_speed_k": "Bleed speed factor",
                     "satiety_v_sleep": "Satiety loss when sleeping",
                     "radiation_v_sleep": "Radiation reduction when sleeping",
                     "satiety_power_v_sleep": "Satiety stamina drop factor wheen sleeping",
                     "satiety_health_v_sleep": "Satiety health drop factor when sleeping",
                     "radiation_health_v_sleep": "Radiation health decrease factor when sleeping",
                     "morale_v_sleep": "Morale recovery rate when sleeping",
                     "psy_health_v_sleep": "Psy-health recovery rate when sleeping",
                     "alcohol_v_sleep": "Alcohol level recovery rate when sleeping",
                     "max_power_leak_speed_sleep": "Fatigue accumulation per second when sleeping (recovery of max stamina)",

                     "bleeding_v_sleep": "Blood loss when sleeping",
                     "wound_incarnation_v_sleep": "Wound healing when sleeping",
                     "health_restore_v": "Health restoration speed",

                     "jump_power": "Jump stamina cost (without weight)",
                     "jump_weight_power": "Jump stamina cost for highest available weight",
                     "overweight_jump_k": "Overburdened jump cost factor",
                     "stand_power": "Stamina loss rate when standing",
                     "walk_power": "Stamina loss rate when walking",
                     "walk_weight_power": "Stamina loss rate when walking with highes allowable weight",
                     "overweight_walk_k": "Stamina loss factor when walking overencumbered",
                     "accel_k": "Stamina loss factor when running",
                     "sprint_k": "Stamina loss factor when running",

                     "limping_health_begin": "Health at which limping starts",
                     "limping_health_end": "Health at which limping ends",
                     "limping_power_begin": "Stamina level at which limping starts",
                     "limping_power_end": "Stamina level at which limping ends",
                     "use_limping_state": "Use limping",
                     "cant_walk_power_begin": "Stamina level at which you cannot walk starts",
                     "cant_walk_power_end": "Stamina level at which you cannot walk ends",
                     "cant_sprint_power_begin": "Stamina level at which you cannot sprint starts",
                     "cant_sprint_power_end": "Stamina level at which you cannot sprint ends",
                     "hud_health_blink": "Health at which HUD starts blinking",

                     "max_power_restore_speed": "Maximum stamina recovery rate",
                     "max_fire_wound_protection": "Maximum value for firearms damage protection",
                     "max_wound_protection":	"Maximum value for rupture damage protection",
                     "radio_zone_max_power": "Maximum value for radiation protection",
                     "fire_zone_max_power": "Maximum value for fire damage protection",
                     "acid_zone_max_power": "Maximum value for acid damage protection",
                     "psi_zone_max_power": "Maximum value for telepathic damage protection",
                     "electra_zone_max_power": "Maximum value for electricity damage protection",
                     }


global_parameters = {}

global_entries = {}

artifact_simple_names = {"burn_immunity": "Burn damage protection",
                         "telepatic_immunity": "Telepathic damage protection",
                         "strike_immunity": "Impact damage protection",
                         "wound_immunity": "Rupture damage protection",
                         "explosion_immunity": "Explosion damage protection",
                         "chemical_burn_immunity": "Chemical burn damage protection",
                         "shock_immunity": "Shock damage protection",
                         "fire_wound_immunity": "Bullet damage protection",
                         "radiation_immunity": "Radiation damage protection",
                         }


minimal_values = {
    "radiation_restore_speed": -50,
    "%": -200,
    "H/mm2": -800,
    "kV": -1000,
    "ml/min": -2000,
    "mSv/sec": -300,
    "burn_immunity": 0,
    "telepatic_immunity": 0,
    "strike_immunity": 0,
    "wound_immunity": 0,
    "explosion_immunity": 0,
    "chemical_burn_immunity": 0,
    "shock_immunity": 0,
    "fire_wound_immunity": 0,
    "radiation_immunity": 0,
    "burn_protection": 0,
    "telepatic_protection": 0,
    "strike_protection": 0,
    "wound_protection": 0,
    "explosion_protection": 0,
    "chemical_burn_protection": 0,
    "shock_protection": 0,
    "fire_wound_protection": 0,
    "radiation_protection": 0,
}


steps_values = {"radiation_restore_speed": 1}

sliders = [
    "burn_protection",
    "shock_protection",
    "radiation_protection",
    "chemical_burn_protection",
    "telepatic_protection",
    "strike_protection",
    "explosion_protection",
    "fire_wound_protection",
    "wound_protection",
    "burn_immunity",
    "telepatic_immunity",
    "strike_immunity",
    "wound_immunity",
    "explosion_immunity",
    "chemical_burn_immunity",
    "shock_immunity",
    "fire_wound_immunity",
    "radiation_immunity",
    "radiation_restore_speed",
    'eat_satiety',
    'eat_radiation',
    'boost_radiation_restore',
    'boost_chemburn_protection',
    'boost_power_restore',
    'boost_telepat_protection',
    'boost_radiation_protection',
    'boost_bleeding_restore',
    'boost_health_restore',
]

switches = ["sprint_allowed",
            "helmet_avaliable",
            "backpack_avaliable",
            "cooking_part",
            "allow_repair",
            "use_condition",
            "dont_stack",
            "remove_after_use",
            "can_trade",
            "default_to_ruck",
            ]

selections = {
    "repair_parts_sections": ["repair_part_bonus"],
    "parts": ["tch_part", "tch_junk"],
    "helmets": ["tch_helmet"],
    "booklets": ["tch_letter"],
    "all": ["identity_immunities", "outfit_actions", "sect_backpack_immunities"],
    "tools": ["itm_basickit"],
    "ammo_class": ["k_bullet_speed"],
    "silencer_name": ["bullet_hit_power_k"]
}


tools = {1: "itm_basickit",
         2: "itm_advancedkit",
         3: "itm_expertkit",
         4: "itm_drugkit",
         5: "itm_ammokit",
         }


artifact_params_coeffs = {'telepatic_immunity': 23200,
                          'radiation_restore_speed': 47000,
                          'burn_immunity': 74000,
                          'chemical_burn_immunity': 76000,
                          'shock_immunity': 2000,
                          'strike_immunity': 2500,
                          'wound_immunity': 2500,
                          'explosion_immunity': 2500,
                          'fire_wound_immunity': 2500,
                          'bleeding_restore_speed': 15000,
                          'power_restore_speed': 30000,
                          'health_restore_speed': 13000,
                          'radiation_immunity': 13000
                          }

armor_params_coeffs = {'burn_protection': 870,
                       'shock_protection': 250,
                       'radiation_protection': 18182,
                       'chemical_burn_protection': 4000,
                       'telepatic_protection': 4000,
                       'strike_protection': 1000,
                       'explosion_protection': 1000,
                       'fire_wound_protection': 1000,
                       'wound_protection': 455
                       }

food_params_coeffs = {'eat_satiety': 1000,
                      'eat_radiation': 12000,
                      'boost_radiation_restore': -30000,
                      'boost_chemburn_protection': 100000,
                      'boost_power_restore': 100000,
                      'boost_telepat_protection': 6000,
                      'boost_radiation_protection': 220000,
                      'boost_bleeding_restore': 150000,
                      'boost_health_restore': 1000
                      }

maximal_values = {
    "radiation_restore_speed": 50,
    "%": 300,
    "H/mm2": 800,
    "kV": 1000,
    "ml/min": 2000,
    "mSv/sec": 300
}

artifact_units = {'telepatic_immunity': "%",
                  'radiation_restore_speed': "mSv/sec",
                  'burn_immunity': "%",
                  'chemical_burn_immunity': "%",
                  'shock_immunity': "kV",
                  'strike_immunity': "H/mm2",
                  'wound_immunity': "H/mm2",
                  'explosion_immunity': "H/mm2",
                  'fire_wound_immunity': "H/mm2",
                  'bleeding_restore_speed': "ml/min",
                  'power_restore_speed': "%",
                  'health_restore_speed': "%",
                  "radiation_immunity": "%",
                  'eat_satiety': "kcal",
                  'eat_radiation': "mSv",
                  'boost_radiation_restore': "mSv/sec",
                  'boost_chemburn_protection': "%",
                  'boost_power_restore': "ug Adrenaline",
                  'boost_telepat_protection': "%",
                  'boost_radiation_protection': "mSv/sec",
                  'boost_bleeding_restore': "ml/h",
                  'boost_health_restore': "%"
                  }

food_units = {'telepatic_immunity': "%",
                  'radiation_restore_speed': "mSv/sec",
                  'bleeding_restore_speed': "ml/min",
                  'power_restore_speed': "%",
                  'health_restore_speed': "%",
                  'eat_satiety': "kcal",
                  'eat_radiation': "mSv",
                  'boost_radiation_restore': "mSv/sec",
                  'boost_chemburn_protection': "%",
                  'boost_power_restore': "ug Adrenaline",
                  'boost_telepat_protection': "%",
                  'boost_radiation_protection': "mSv/sec",
                  'boost_bleeding_restore': "ml/h",
                  'boost_health_restore': "%"
                  }

parameter_icons = {"health_restore_speed": (498, 110),
                   "radiation_restore_speed": (498, 130),
                   "satiety_restore_speed": (498, 150),
                   "bleeding_restore_speed": (498, 170),
                   "power_restore_speed": (498, 190),
                   "shock": (518, 110),
                   "burn": (518, 130),
                   "strike": (518, 150),
                   "wound": (518, 170),
                   "radiation": (518, 190),
                   "telepatic": (538, 110),
                   "chemical_burn": (538, 130),
                   "explosion": (538, 150),
                   "fire_wound": (538, 170),
                   "additional_weight": (538, 190),
}

sections = {"Ammo": ['ammo', 'ammo_bad', 'ammo_damaged'],
            "Armor": ['headgear', 'outfits', 'outfits_ecolog'],
            "Artifacts": ['artefacts', 'mutant_parts', 'artefacts_h'],
            "Consumables": ['drugs', 'cigs', 'drinks', "food", "mutant_parts"],
            "Devices": ['devices', 'backpacks', "cooking_stuff"],
            "Tools": ['tools', 'repair_kits', 'upgrade_items', "parts", "toolkits_h"],
            "Weapons": ['pistols', 'rifles', 'melee', "explosives", "w_addons"],
            "Other": ['money', 'camping', 'common_stock', "misc", "unused", "trash", "fuels"]
            }

basic_sections = {"Ammo": ['ammo'],
                  "Armor": ['armor'],
                  "Artifacts": ['artifact'],
                  "Consumables": ["food"],
                  "Devices": ['device'],
                  "Tools": ['repair'],
                  "Weapons": ["weapon"],
                  "Other": ["base"]
                  }