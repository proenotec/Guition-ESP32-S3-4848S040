#!/usr/bin/env python3
"""
ESPHome LVGL Light UI Generator
Generates light_ui_lvgl.yaml based on substitutions.yaml configuration
"""

import yaml
import sys

# Custom YAML class to represent ESPHome !lambda tags
class Lambda:
    """Represents an ESPHome !lambda expression"""
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"Lambda({self.expression})"

# Custom YAML representer for Lambda objects
def lambda_representer(dumper, data):
    return dumper.represent_scalar('!lambda', data.expression, style='')

# Register the custom representer
yaml.add_representer(Lambda, lambda_representer)

def load_substitutions(filename='substitutions.yaml'):
    """Load substitutions from YAML file"""
    with open(filename, 'r') as f:
        return yaml.safe_load(f)

def generate_light_button(index, icon_var, lights_amount):
    """Generate a single light button widget"""
    btn_id = f"light_btn_{index}"
    icon_id = f"light_icon_{index}"

    # Generate shadow_color updates ONLY for active buttons (1 to lights_amount)
    shadow_updates = []
    for i in range(1, lights_amount + 1):
        shadow_updates.append({
            'lvgl.obj.update': {
                'id': f'light_btn_{i}',
                'shadow_color': 'color_misty_blue' if i == index else 'color_black'
            }
        })

    return {
        'obj': {
            'id': btn_id,
            'width': 48,
            'height': 48,
            'pad_all': 0,
            'radius': 30,
            'bg_opa': 'transp',
            'border_opa': 'transp',
            'shadow_width': 5,
            'shadow_spread': 1,
            'shadow_color': 'color_black',
            'pressed': {
                'bg_color': 'color_black',
                'shadow_width': 4
            },
            'widgets': [{
                'label': {
                    'id': icon_id,
                    'align': 'center',
                    'text_font': 'icons_24',
                    'text_color': 'color_misty_blue',
                    'text': f'${{{icon_var}}}'
                }
            }],
            'on_press': [
                {
                    'script.execute': {
                        'id': 'light_switch_index',
                        'position': index
                    }
                },
                {'lvgl.page.show': 'light_control_page'}
            ] + shadow_updates
        }
    }

def generate_light_ui(substitutions):
    """Generate complete LVGL light UI configuration"""
    lights_amount = int(substitutions.get('lights_amount', 5))

    # Base LVGL structure with gradients
    lvgl_config = {
        'lvgl': {
            'gradients': [
                {
                    'id': 'light_hue_gradient',
                    'direction': 'ver',
                    'dither': 'none',
                    'stops': [
                        {'color': 16711680, 'position': 0},
                        {'color': 16776960, 'position': 43},
                        {'color': 65280, 'position': 85},
                        {'color': 65535, 'position': 128},
                        {'color': 255, 'position': 171},
                        {'color': 16711935, 'position': 213},
                        {'color': 16711680, 'position': 255}
                    ]
                },
                {
                    'id': 'light_color_temp_gradient',
                    'direction': 'ver',
                    'dither': 'none',
                    'stops': [
                        {'color': 10537215, 'position': 0},
                        {'color': 14743551, 'position': 80},
                        {'color': 16777215, 'position': 128},
                        {'color': 16777184, 'position': 175},
                        {'color': 16766624, 'position': 255}
                    ]
                }
            ],
            'on_boot': {
                'then': [
                    {'script.execute': 'light_init'},
                    {
                        'lvgl.obj.update': {
                            'id': 'light_btn_1',
                            'shadow_color': 'color_misty_blue'
                        }
                    },
                    {'delay': '1s'},
                    {'script.execute': 'light_update_all_selector_icons'}
                ]
            },
            'top_layer': {
                'widgets': [{
                    'obj': {
                        'id': 'light_select_widget',
                        'hidden': True,
                        'x': -40,
                        'y': -40,
                        'width': 465,
                        'height': 110,
                        'align': 'top_left',
                        'pad_all': 0,
                        'bg_color': 'color_slate_blue_gray',
                        'bg_opa': 'cover',
                        'border_opa': 'transp',
                        'border_width': 0,
                        'shadow_color': 'color_black',
                        'shadow_spread': 3,
                        'shadow_width': 8,
                        'scrollable': False,
                        'radius': 40,
                        'widgets': [{
                            'obj': {
                                'id': 'light_select_widget_cont',
                                'x': -10,
                                'y': -5,
                                'width': 405,
                                'height': 60,
                                'align': 'bottom_right',
                                'bg_opa': 'transp',
                                'border_opa': 'transp',
                                'border_width': 0,
                                'pad_all': 0,
                                'layout': {
                                    'type': 'flex',
                                    'flex_align_main': 'space_evenly',
                                    'flex_align_cross': 'center',
                                    'flex_align_track': 'center'
                                },
                                'widgets': []
                            }
                        }]
                    }
                }]
            },
            'pages': [{
                'id': 'light_control_page',
                'bg_color': 'color_slate_blue_gray',
                'on_load': [
                            # ✅ Método centralizado
        - script.execute:
            id: set_active_page
            page_name: "light_control_page"
                    {'script.execute': 'light_update_layout'},
                    {'delay': '200ms'},
                    {'script.execute': 'light_update_lightbulb_color'},
                    {'script.execute': 'light_update_button_icon_color'}
                ],
                'widgets': [
                    # Brightness slider
                    {
                        'obj': {
                            'id': 'light_brightness_background',
                            'x': -160,
                            'y': 0,
                            'radius': 20,
                            'width': 80,
                            'height': 260,
                            'align': 'center',
                            'bg_color': 'color_slate_blue_gray',
                            'pad_all': 0,
                            'border_opa': 'transp',
                            'border_width': 0,
                            'shadow_color': 'color_black',
                            'shadow_spread': 2,
                            'shadow_width': 8,
                            'widgets': [{
                                'slider': {
                                    'id': 'light_brightness_slider',
                                    'radius': 16,
                                    'width': 60,
                                    'height': 240,
                                    'align': 'center',
                                    'bg_color': 'color_steel_blue',
                                    'shadow_color': 'color_black',
                                    'shadow_spread': 4,
                                    'shadow_width': 6,
                                    'shadow_opa': 'transp',
                                    'min_value': 2,
                                    'max_value': 255,
                                    'indicator': {
                                        'bg_color': 'color_deep_orange',
                                        'radius': 10
                                    },
                                    'knob': {
                                        'bg_opa': 'transp'
                                    },
                                    'on_value': [
                                        {
                                            'globals.set': {
                                                'id': 'light_current_brightness',
                                                'value': Lambda('return x;')
                                            }
                                        },
                                        {'script.execute': 'light_update_lightbulb_color'},
                                        {'script.execute': 'light_update_button_icon_color'}
                                    ],
                                    'on_release': [{
                                        'homeassistant.action': {
                                            'action': 'light.turn_on',
                                            'data': {
                                                'entity_id': Lambda('return id(current_light_entity);'),
                                                'brightness': Lambda('return int(x);')
                                            }
                                        }
                                    }]
                                }
                            }]
                        }
                    },
                    # Saturation slider
                    {
                        'obj': {
                            'id': 'light_saturation_background',
                            'x': -60,
                            'y': 0,
                            'radius': 20,
                            'width': 80,
                            'height': 260,
                            'align': 'center',
                            'bg_color': 'color_slate_blue_gray',
                            'pad_all': 0,
                            'border_opa': 'transp',
                            'border_width': 0,
                            'shadow_color': 'color_black',
                            'shadow_spread': 2,
                            'shadow_width': 8,
                            'widgets': [{
                                'slider': {
                                    'id': 'light_saturation_slider',
                                    'radius': 16,
                                    'width': 60,
                                    'height': 240,
                                    'align': 'center',
                                    'bg_color': 'color_steel_blue',
                                    'shadow_color': 'color_black',
                                    'shadow_spread': 4,
                                    'shadow_width': 6,
                                    'shadow_opa': 'transp',
                                    'min_value': 0,
                                    'max_value': 100,
                                    'indicator': {
                                        'bg_color': 'color_red',
                                        'radius': 10
                                    },
                                    'knob': {
                                        'bg_opa': 'transp'
                                    },
                                    'on_value': [
                                        {
                                            'globals.set': {
                                                'id': 'light_current_saturation',
                                                'value': Lambda('return x;')
                                            }
                                        },
                                        {'script.execute': 'light_update_lightbulb_color'},
                                        {'script.execute': 'light_update_button_icon_color'}
                                    ],
                                    'on_release': [{
                                        'homeassistant.action': {
                                            'action': 'light.turn_on',
                                            'data': {
                                                'entity_id': Lambda('return id(current_light_entity);')
                                            },
                                            'data_template': {
                                                'hs_color': '"{{ (hue|float, sat|float)|list }}"'
                                            },
                                            'variables': {
                                                'hue': Lambda('return id(light_current_hue);'),
                                                'sat': Lambda('return x;')
                                            }
                                        }
                                    }]
                                }
                            }]
                        }
                    },
                    # Light name label
                    {
                        'label': {
                            'id': 'light_name_label',
                            'y': -30,
                            'x': 0,
                            'height': 40,
                            'width': 240,
                            'long_mode': 'dot',
                            'align': 'bottom_left',
                            'text_font': 'nunito_20',
                            'text_align': 'center',
                            'text_color': 'color_misty_blue',
                            'text': 'Light'
                        }
                    },
                    # Main temperature control background (with nested widgets)
                    {
                        'obj': {
                            'id': 'light_bg_main_temperature',
                            'hidden': False,
                            'width': 240,
                            'height': 480,
                            'align': 'right_mid',
                            'pad_all': 0,
                            'bg_opa': 'transp',
                            'clickable': False,
                            'scrollable': False,
                            'border_opa': 'transp',
                            'border_width': 0,
                            'shadow_opa': 'transp',
                            'widgets': [{
                                'obj': {
                                    'x': 240,
                                    'width': 480,
                                    'height': 480,
                                    'scrollable': False,
                                    'align': 'right_mid',
                                    'pad_all': 0,
                                    'bg_opa': 'transp',
                                    'shadow_opa': 'transp',
                                    'border_opa': 'transp',
                                    'border_width': 0,
                                    'widgets': [
                                        {
                                            'obj': {
                                                'width': 460,
                                                'height': 460,
                                                'align': 'center',
                                                'clickable': True,
                                                'radius': 260,
                                                'bg_opa': 'transp',
                                                'bg_color': 'color_slate_blue_gray',
                                                'border_color': 'color_black',
                                                'border_opa': '40%',
                                                'border_width': 3
                                            }
                                        },
                                        {
                                            'obj': {
                                                'id': 'light_hue_gradient_obj',
                                                'hidden': True,
                                                'x': 222,
                                                'width': 444,
                                                'height': 444,
                                                'radius': 222,
                                                'align': 'right_mid',
                                                'pad_all': 0,
                                                'bg_grad': 'light_hue_gradient',
                                                'bg_grad_dir': 'ver',
                                                'shadow_opa': 'transp',
                                                'border_opa': 'transp',
                                                'border_width': 0
                                            }
                                        },
                                        {
                                            'obj': {
                                                'id': 'light_color_temp_gradient_obj',
                                                'x': 222,
                                                'width': 444,
                                                'height': 444,
                                                'radius': 222,
                                                'align': 'right_mid',
                                                'pad_all': 0,
                                                'bg_grad': 'light_color_temp_gradient',
                                                'bg_grad_dir': 'ver',
                                                'shadow_opa': 'transp',
                                                'border_opa': 'transp',
                                                'border_width': 0
                                            }
                                        },
                                        {
                                            'obj': {
                                                'x': 188,
                                                'width': 376,
                                                'height': 376,
                                                'align': 'right_mid',
                                                'clickable': False,
                                                'radius': 230,
                                                'bg_color': 'color_slate_blue_gray',
                                                'border_width': 0,
                                                'border_opa': 'transp'
                                            }
                                        },
                                        {
                                            'obj': {
                                                'x': 183,
                                                'width': 366,
                                                'height': 366,
                                                'align': 'right_mid',
                                                'radius': 230,
                                                'bg_color': 'color_slate_blue_gray',
                                                'border_color': 'color_white',
                                                'border_width': 3,
                                                'border_opa': '15%'
                                            }
                                        },
                                        {
                                            'obj': {
                                                'x': 222,
                                                'width': 444,
                                                'height': 444,
                                                'radius': 222,
                                                'align': 'right_mid',
                                                'pad_all': 0,
                                                'bg_opa': 'transp',
                                                'shadow_opa': 'transp',
                                                'border_opa': 'transp',
                                                'border_width': 0,
                                                'widgets': [
                                                    {
                                                        'arc': {
                                                            'id': 'light_arc_hue',
                                                            'hidden': True,
                                                            'clickable': True,
                                                            'adjustable': True,
                                                            'adv_hittest': True,
                                                            'align': 'center',
                                                            'width': 444,
                                                            'height': 444,
                                                            'start_angle': 0,
                                                            'end_angle': 180,
                                                            'min_value': 0,
                                                            'max_value': 360,
                                                            'value': 265,
                                                            'arc_width': 34,
                                                            'rotation': 90.0,
                                                            'arc_opa': 'transp',
                                                            'indicator': {
                                                                'arc_opa': 'transp',
                                                                'arc_width': 34
                                                            },
                                                            'knob': {
                                                                'pad_all': 0,
                                                                'bg_opa': 'transp',
                                                                'border_color': 'color_steel_blue',
                                                                'border_width': 4,
                                                                'shadow_opa': 'transp'
                                                            },
                                                            'on_value': [
                                                                {
                                                                    'globals.set': {
                                                                        'id': 'light_current_hue',
                                                                        'value': Lambda('return x;')
                                                                    }
                                                                },
                                                                {'script.execute': 'light_update_lightbulb_color'},
                                                                {'script.execute': 'light_update_button_icon_color'}
                                                            ],
                                                            'on_release': [{
                                                                'homeassistant.action': {
                                                                    'action': 'light.turn_on',
                                                                    'data': {
                                                                        'entity_id': Lambda('return id(current_light_entity);')
                                                                    },
                                                                    'data_template': {
                                                                        'hs_color': '"{{ (hue|float, sat|float)|list }}"'
                                                                    },
                                                                    'variables': {
                                                                        'hue': Lambda('return x;'),
                                                                        'sat': Lambda('return id(light_current_saturation);')
                                                                    }
                                                                }
                                                            }]
                                                        }
                                                    },
                                                    {
                                                        'arc': {
                                                            'id': 'light_arc_color_temp',
                                                            'hidden': False,
                                                            'clickable': True,
                                                            'adjustable': True,
                                                            'adv_hittest': True,
                                                            'align': 'center',
                                                            'width': 444,
                                                            'height': 444,
                                                            'start_angle': 0,
                                                            'end_angle': 180,
                                                            'min_value': 2000,
                                                            'max_value': 6500,
                                                            'value': 3000,
                                                            'arc_width': 34,
                                                            'rotation': 90.0,
                                                            'arc_opa': 'transp',
                                                            'indicator': {
                                                                'arc_opa': 'transp',
                                                                'arc_width': 34
                                                            },
                                                            'knob': {
                                                                'pad_all': 0,
                                                                'bg_opa': 'transp',
                                                                'border_color': 'color_steel_blue',
                                                                'border_width': 4,
                                                                'shadow_opa': 'transp'
                                                            },
                                                            'on_value': [
                                                                {
                                                                    'globals.set': {
                                                                        'id': 'light_current_color_temp',
                                                                        'value': Lambda('return x;')
                                                                    }
                                                                },
                                                                {'script.execute': 'light_update_lightbulb_color'},
                                                                {'script.execute': 'light_update_button_icon_color'}
                                                            ],
                                                            'on_release': [{
                                                                'homeassistant.action': {
                                                                    'action': 'light.turn_on',
                                                                    'data': {
                                                                        'entity_id': Lambda('return id(current_light_entity);'),
                                                                        'color_temp_kelvin': Lambda('return int(x);')
                                                                    }
                                                                }
                                                            }]
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }]
                        }
                    },
                    # LIGHTBULB BUTTON - This is a SIBLING of light_bg_main_temperature at page widgets level
                    {
                        'obj': {
                            'id': 'light_lightbulb_btn',
                            'x': 0,
                            'width': 160,
                            'height': 160,
                            'align': 'right_mid',
                            'bg_opa': 'transp',
                            'pad_all': 0,
                            'border_opa': 'transp',
                            'border_width': 0,
                            'shadow_opa': 'transp',
                            'radius': 100,
                            'widgets': [
                                {
                                    'obj': {
                                        'id': 'light_lightbulb_obj',
                                        'clickable': False,
                                        'x': 0,
                                        'y': -30,
                                        'width': 70,
                                        'height': 70,
                                        'radius': 35,
                                        'align': 'center',
                                        'bg_color': 'color_light_gray',
                                        'border_opa': 'transp',
                                        'shadow_opa': 'transp'
                                    }
                                },
                                {
                                    'image': {
                                        'id': 'light_lightbulb_image',
                                        'x': 0,
                                        'y': 23,
                                        'align': 'center',
                                        'src': 'lightbulb_image'
                                    }
                                },
                                {
                                    'label': {
                                        'id': 'light_icon_label',
                                        'align': 'center',
                                        'y': -30,
                                        'text_font': 'icons_40',
                                        'text_color': 'color_misty_blue',
                                        'text': '${lightbulb}'
                                    }
                                }
                            ]
                        }
                    },
                    # Back button
                    {
                        'obj': {
                            'id': 'light_back_btn',
                            'x': 150,
                            'y': 0,
                            'width': 80,
                            'height': 70,
                            'align': 'bottom_left',
                            'bg_opa': 'transp',
                            'pad_all': 0,
                            'border_opa': 'transp',
                            'border_width': 0,
                            'shadow_opa': 'transp',
                            'radius': 0,
                            'widgets': [{
                                'obj': {
                                    'y': -20,
                                    'width': 80,
                                    'height': 5,
                                    'align': 'bottom_mid',
                                    'bg_color': 'color_steel_blue',
                                    'pad_all': 0,
                                    'border_opa': 'transp',
                                    'border_width': 0,
                                    'shadow_opa': 'transp',
                                    'radius': 15
                                }
                            }],
                            'on_click': [
                                {  'lvgl.widget.hide': 'light_select_widget'},
                                {  'delay': '100ms'},
            - script.execute:
                id: page_cleanup
                page_name: "texto_page"
                                {  'lvgl.page.show': 'home_page'}
                            ]
                        }
                    }
                ]
            }]
        }
    }

    # Generate light buttons dynamically based on lights_amount
    buttons_widgets = []
    for i in range(1, lights_amount + 1):
        icon_var = f'light_icon_{i}'
        buttons_widgets.append(generate_light_button(i, icon_var, lights_amount))

    # Insert buttons into the container
    lvgl_config['lvgl']['top_layer']['widgets'][0]['obj']['widgets'][0]['obj']['widgets'] = buttons_widgets

    return lvgl_config

def main():
    """Main execution function"""
    try:
        # Load substitutions
        substitutions = load_substitutions('substitutions.yaml')

        # Generate light UI configuration
        light_ui = generate_light_ui(substitutions)

        # Write to output file with proper formatting
        with open('light_ui_lvgl_generated.yaml', 'w') as f:
            yaml.dump(light_ui, f, default_flow_style=False, sort_keys=False, width=120, allow_unicode=True)

        print(f"✓ Successfully generated light_ui_lvgl_generated.yaml")
        print(f"  Lights configured: {substitutions.get('lights_amount', 5)}")
        print(f"  !lambda expressions properly formatted")
        print(f"  light_lightbulb_btn at correct hierarchy level")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
