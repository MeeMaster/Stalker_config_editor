
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
                     "burn_immunity": "Burn damage degradation factor",
                     "telepatic_immunity": "Telepathic damage degradation factor",
                     "strike_immunity": "Impact damage degradation factor",
                     "wound_immunity": "Rupture damage degradation factor",
                     "explosion_immunity": "Explosion damage degradation factor",
                     "chemical_burn_immunity": "Chemical burn damage degradation factor",
                     "shock_immunity": "Shock damage degradation factor",
                     "fire_wound_immunity": "Bullet damage degradation factor",
                     "radiation_immunity": "Radiation damage degradation factor",
                     "rpm": "Fire rate",
                     "fire_dispersion_base": "Weapon spread",
                     "fire_modes": "Fire modes",
                     "ammo_mag_size": "Mag size",
                     "silencer_name": "Matching silencer",
                     "fire_distance": "Weapon range",
                     "bullet_speed": "Bullet speed",
                     "hit_impulse": "Weapon hit stagger",
                     "hit_power": "Recoil power",
                     "repair_only": "Repairs",
                     "repair_min_condition": "Minimum repair condition",
                     "repair_add_condition": "Repair value",
                     "repair_part_bonus": "Bonus repair points",
                     "use_condition": "Condition degradation",
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


                     }

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

selections = {
    "repair_parts_sections": "repair_part_bonus"
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
            "Devices": ['devices', 'backpacks'],
            "Equipment": ['headgear', 'outfits', 'outfits_ecolog'],
            "Tools": ['tools', 'repair_kits', 'upgrade_items', "parts", "toolkits_h"],
            "Weapons": ['pistols', 'rifles', 'melee', "explosives"],
            "Other": ['money', 'camping', 'common_stock', "misc", "unused"]
            }