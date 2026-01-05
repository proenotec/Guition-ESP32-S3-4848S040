#!/usr/bin/env python3
"""
ESPHome Light Configuration Generator
Generates light.yaml based on lights_amount from substitutions.yaml
"""

import yaml
import sys

def load_substitutions(file_path='substitutions.yaml'):
    """Load substitutions from YAML file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def write_yaml_header(f):
    """Write the YAML header with proper syntax"""
    f.write('substitutions: !include substitutions.yaml\n\n')
    f.write('packages:\n')
    f.write('  lights_scr: !include light_scripts.yaml\n')
    f.write('  lvgl_scr: !include lvgl_scripts.yaml\n')
    f.write('  # Include LVGL display UI section\n')
    f.write('  lvgl_ui: !include light_ui_lvgl_generated.yaml\n\n')

def write_globals(f, lights_amount):
    """Write globals section"""
    f.write('globals:\n')

    # Per-light capability flags
    for i in range(1, lights_amount + 1):
        f.write(f'  - id: light_{i}_supports_color_temp\n')
        f.write('    type: bool\n')
        f.write("    initial_value: 'false'\n")

        f.write(f'  - id: light_{i}_supports_hs\n')
        f.write('    type: bool\n')
        f.write("    initial_value: 'false'\n")

        f.write(f'  - id: light_{i}_supports_rgb\n')
        f.write('    type: bool\n')
        f.write("    initial_value: 'false'\n")

        f.write(f'  - id: light_{i}_supports_brightness\n')
        f.write('    type: bool\n')
        f.write("    initial_value: 'false'\n")

    # Stored light names
    for i in range(1, lights_amount + 1):
        f.write(f'  - id: light_name_{i}_stored\n')
        f.write('    type: std::string\n')
        f.write('    initial_value: \'\"\"\'\n')
        f.write('    restore_value: no\n')

    # Common globals
    f.write('  - id: current_light_index\n')
    f.write('    type: int\n')
    f.write("    initial_value: '1'\n")
    f.write('    restore_value: no\n')

    f.write('  - id: current_light_entity\n')
    f.write('    type: std::string\n')
    f.write('    initial_value: \'"${light_entity_1}"\'\n')
    f.write('    restore_value: no\n')

    f.write('  - id: light_initial_load_complete\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_supports_color_temp\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_supports_hs\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_supports_rgb\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_supports_brightness\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_is_temp_mode\n')
    f.write('    type: bool\n')
    f.write("    initial_value: 'false'\n")

    f.write('  - id: light_current_hue\n')
    f.write('    type: float\n')
    f.write("    initial_value: '0.0'\n")

    f.write('  - id: light_current_saturation\n')
    f.write('    type: float\n')
    f.write("    initial_value: '0.0'\n")

    f.write('  - id: light_current_brightness\n')
    f.write('    type: int\n')
    f.write("    initial_value: '100'\n")

    f.write('  - id: light_current_color_temp\n')
    f.write('    type: float\n')
    f.write("    initial_value: '3000.0'\n")

    f.write('\n')

def write_binary_sensors(f, lights_amount):
    """Write binary_sensor section"""
    f.write('binary_sensor:\n')

    # Per-light state sensors
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_state_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    internal: true\n')
        f.write('    trigger_on_initial_state: true\n')
        f.write('    on_state:\n')
        f.write('      - script.execute: light_update_all_selector_icons\n')
        f.write('      - script.execute: update_home_lights_btn_color\n')

    # Template for current light state
    f.write('  - platform: template\n')
    f.write('    id: light_state\n')
    f.write('    lambda: |-\n')
    f.write('      auto get_state = [&](int idx) -> bool {\n')
    f.write('        switch (idx) {\n')
    for i in range(1, lights_amount + 1):
        f.write(f'          case {i}: return id(light_state_{i}).state;\n')
    f.write('          default: return false;\n')
    f.write('        }\n')
    f.write('      };\n')
    f.write('      return get_state(id(current_light_index));\n')
    f.write('    on_press:\n')
    f.write('      - script.execute: light_update_lightbulb_color\n')
    f.write('      - script.execute: light_update_button_icon_color\n')
    f.write('    on_release:\n')
    f.write('      - script.execute: light_update_lightbulb_color\n')
    f.write('      - script.execute: light_update_button_icon_color\n')

    # LVGL button control
    f.write('  - platform: lvgl\n')
    f.write('    id: light_btn_control\n')
    f.write('    widget: light_lightbulb_btn\n')
    f.write('    on_click:\n')
    f.write('      - min_length: 50ms\n')
    f.write('        max_length: 500ms\n')
    f.write('        then:\n')
    f.write('          - lambda: \'ESP_LOGD("light_btn", "Short press - toggling light");\'\n')
    f.write('          - homeassistant.service:\n')
    f.write('              service: homeassistant.toggle\n')
    f.write('              data:\n')
    f.write('                entity_id: !lambda \'return id(current_light_entity);\'\n')
    f.write('      - min_length: 800ms\n')
    f.write('        max_length: 3000ms\n')
    f.write('        then:\n')
    f.write('          - if:\n')
    f.write('              condition:\n')
    f.write('                lambda: |-\n')
    f.write('                  return id(light_supports_color_temp) &&\n')
    f.write('                         (id(light_supports_hs) || id(light_supports_rgb));\n')
    f.write('              then:\n')
    f.write('                - lambda: |-\n')
    f.write('                    id(light_is_temp_mode) = !id(light_is_temp_mode);\n')
    f.write('                    ESP_LOGD("light_btn", "Long press - switching mode to: %s",\n')
    f.write('                             id(light_is_temp_mode) ? "ColorTemp" : "HS");\n')
    f.write('                - script.execute: light_toggle_gradient\n')
    f.write('              else:\n')
    f.write('                - lambda: \'ESP_LOGD("light_btn", "Long press ignored - only one color mode supported");\'\n')

    f.write('\n')

def write_brightness_sensors(f, lights_amount):
    """Write brightness sensors"""
    # Per-light brightness
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_brightness_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    attribute: brightness\n')
        f.write('    internal: true\n')
        f.write('    on_value:\n')
        f.write('      - if:\n')
        f.write('          condition:\n')
        f.write(f'            lambda: \'return id(current_light_index) == {i};\'\n')
        f.write('          then:\n')
        f.write('            - sensor.template.publish:\n')
        f.write('                id: light_brightness\n')
        f.write('                state: !lambda \'return x;\'\n')
        f.write('            - script.execute: light_update_all_selector_icons\n')

    # Template for current brightness
    f.write('  - platform: template\n')
    f.write('    id: light_brightness\n')
    f.write('    internal: true\n')
    f.write('    lambda: |-\n')
    f.write('      auto get_brightness = [&](int idx) -> optional<float> {\n')
    f.write('        switch (idx) {\n')
    for i in range(1, lights_amount + 1):
        f.write(f'          case {i}: return id(light_brightness_{i}).state;\n')
    f.write('          default: return {};\n')
    f.write('        }\n')
    f.write('      };\n')
    f.write('      return get_brightness(id(current_light_index));\n')
    f.write('    on_value:\n')
    f.write('      - if:\n')
    f.write('          condition:\n')
    f.write('            lambda: \'return !std::isnan(x);\'\n')
    f.write('          then:\n')
    f.write('            - globals.set:\n')
    f.write('                id: light_current_brightness\n')
    f.write('                value: !lambda \'return x;\'\n')
    f.write('            - lvgl.slider.update:\n')
    f.write('                id: light_brightness_slider\n')
    f.write('                value: !lambda \'return int(x);\'\n')
    f.write('            - script.execute: light_update_lightbulb_color\n')
    f.write('            - script.execute: light_update_button_icon_color\n')

def write_color_temp_sensors(f, lights_amount):
    """Write color temperature sensors"""
    # Per-light color temp
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_color_temp_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    attribute: color_temp_kelvin\n')
        f.write('    internal: true\n')
        f.write('    on_value:\n')
        f.write('      - if:\n')
        f.write('          condition:\n')
        f.write(f'            lambda: \'return id(current_light_index) == {i};\'\n')
        f.write('          then:\n')
        f.write('            - sensor.template.publish:\n')
        f.write('                id: light_color_temp\n')
        f.write('                state: !lambda \'return x;\'\n')
        f.write('            - script.execute: light_update_all_selector_icons\n')

    # Template for current color temp
    f.write('  - platform: template\n')
    f.write('    id: light_color_temp\n')
    f.write('    internal: true\n')
    f.write('    lambda: |-\n')
    f.write('      auto get_color_temp = [&](int idx) -> optional<float> {\n')
    f.write('        switch (idx) {\n')
    for i in range(1, lights_amount + 1):
        f.write(f'          case {i}: return id(light_color_temp_{i}).state;\n')
    f.write('          default: return {};\n')
    f.write('        }\n')
    f.write('      };\n')
    f.write('      return get_color_temp(id(current_light_index));\n')
    f.write('    on_value:\n')
    f.write('      - if:\n')
    f.write('          condition:\n')
    f.write('            lambda: \'return !std::isnan(x);\'\n')
    f.write('          then:\n')
    f.write('            - globals.set:\n')
    f.write('                id: light_current_color_temp\n')
    f.write('                value: !lambda \'return x;\'\n')
    f.write('            - lvgl.arc.update:\n')
    f.write('                id: light_arc_color_temp\n')
    f.write('                value: !lambda \'return int(x);\'\n')
    f.write('            - if:\n')
    f.write('                condition:\n')
    f.write('                  lambda: \'return id(light_is_temp_mode);\'\n')
    f.write('                then:\n')
    f.write('                  - script.execute: light_update_lightbulb_color\n')
    f.write('                  - script.execute: light_update_button_icon_color\n')

def write_name_sensors(f, lights_amount):
    """Write friendly name sensors"""
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_name_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    attribute: friendly_name\n')
        f.write('    on_value:\n')
        f.write('      - lambda: |-\n')
        f.write(f'          id(light_name_{i}_stored) = x;\n')
        f.write(f'          ESP_LOGD("light_name", "Stored light {i} name: %s", x.c_str());\n')
        f.write('      - if:\n')
        f.write('          condition:\n')
        f.write(f'            lambda: \'return id(current_light_index) == {i};\'\n')
        f.write('          then:\n')
        f.write('            - lvgl.label.update:\n')
        f.write('                id: light_name_label\n')
        f.write('                text: !lambda \'return x;\'\n')

def write_hs_color_sensors(f, lights_amount):
    """Write HS color sensors"""
    # Per-light HS color
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_hs_color_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    attribute: hs_color\n')
        f.write('    internal: true\n')
        f.write('    on_value:\n')
        f.write('      - if:\n')
        f.write('          condition:\n')
        f.write(f'            lambda: \'return id(current_light_index) == {i};\'\n')
        f.write('          then:\n')
        f.write('            - text_sensor.template.publish:\n')
        f.write('                id: light_hs_color\n')
        f.write('                state: !lambda \'return x;\'\n')
        f.write('            - script.execute: light_update_all_selector_icons\n')

    # Template for current HS color
    f.write('  - platform: template\n')
    f.write('    id: light_hs_color\n')
    f.write('    internal: true\n')
    f.write('    lambda: |-\n')
    f.write('      auto get_hs = [&](int idx) -> std::string {\n')
    f.write('        switch (idx) {\n')
    for i in range(1, lights_amount + 1):
        f.write(f'          case {i}: return id(light_hs_color_{i}).state;\n')
    f.write('          default: return "";\n')
    f.write('        }\n')
    f.write('      };\n')
    f.write('      return get_hs(id(current_light_index));\n')
    f.write('    on_value:\n')
    f.write('      - if:\n')
    f.write('          condition:\n')
    f.write('            lambda: \'return x != "None" && !x.empty();\'\n')
    f.write('          then:\n')
    f.write('            - lambda: |-\n')
    f.write('                std::string s = x;\n')
    f.write('                size_t start = s.find(\'(\') + 1;\n')
    f.write('                size_t comma = s.find(\',\');\n')
    f.write('                size_t end = s.find(\')\');\n')
    f.write('                float hue = 0.0, sat = 0.0;\n')
    f.write('                if (start < comma && comma < end) {\n')
    f.write('                  hue = atof(s.substr(start, comma - start).c_str());\n')
    f.write('                  sat = atof(s.substr(comma + 1, end - comma - 1).c_str());\n')
    f.write('                }\n')
    f.write('                id(light_current_hue) = hue;\n')
    f.write('                id(light_current_saturation) = sat;\n')
    f.write('            - lvgl.arc.update:\n')
    f.write('                id: light_arc_hue\n')
    f.write('                value: !lambda \'return id(light_current_hue);\'\n')
    f.write('            - if:\n')
    f.write('                condition:\n')
    f.write('                  lambda: |-\n')
    f.write('                    return !id(light_is_temp_mode) &&\n')
    f.write('                           (id(light_supports_hs) || id(light_supports_rgb));\n')
    f.write('                then:\n')
    f.write('                  - lvgl.slider.update:\n')
    f.write('                      id: light_saturation_slider\n')
    f.write('                      value: !lambda \'return id(light_current_saturation);\'\n')
    f.write('            - if:\n')
    f.write('                condition:\n')
    f.write('                  lambda: \'return !id(light_is_temp_mode);\'\n')
    f.write('                then:\n')
    f.write('                  - script.execute: light_update_lightbulb_color\n')
    f.write('                  - script.execute: light_update_button_icon_color\n')

def write_supported_modes_sensors(f, lights_amount):
    """Write supported modes sensors"""
    # Per-light supported modes
    for i in range(1, lights_amount + 1):
        f.write('  - platform: homeassistant\n')
        f.write(f'    id: light_supported_modes_{i}\n')
        f.write(f'    entity_id: "${{light_entity_{i}}}"\n')
        f.write('    attribute: supported_color_modes\n')
        f.write('    internal: true\n')
        f.write('    on_value:\n')
        f.write('      - lambda: |-\n')
        f.write('          std::string modes = x;\n')
        f.write(f'          id(light_{i}_supports_color_temp) = (modes.find("color_temp") != std::string::npos);\n')
        f.write(f'          id(light_{i}_supports_hs) = (modes.find("hs") != std::string::npos);\n')
        f.write(f'          id(light_{i}_supports_rgb) = (modes.find("rgb") != std::string::npos);\n')
        f.write(f'          id(light_{i}_supports_brightness) = (\n')
        f.write('            modes.find("brightness") != std::string::npos ||\n')
        f.write(f'            id(light_{i}_supports_hs) ||\n')
        f.write(f'            id(light_{i}_supports_rgb) ||\n')
        f.write(f'            id(light_{i}_supports_color_temp)\n')
        f.write('          );\n')
        f.write(f'          ESP_LOGD("light_widget", "Light {i} modes: temp=%d hs=%d rgb=%d bright=%d",\n')
        f.write(f'                   id(light_{i}_supports_color_temp), id(light_{i}_supports_hs),\n')
        f.write(f'                   id(light_{i}_supports_rgb), id(light_{i}_supports_brightness));\n')
        f.write('      - if:\n')
        f.write('          condition:\n')
        f.write(f'            lambda: \'return id(current_light_index) == {i};\'\n')
        f.write('          then:\n')
        f.write('            - text_sensor.template.publish:\n')
        f.write('                id: light_supported_modes\n')
        f.write('                state: !lambda \'return x;\'\n')

    # Template for current supported modes
    f.write('  - platform: template\n')
    f.write('    id: light_supported_modes\n')
    f.write('    internal: true\n')
    f.write('    lambda: |-\n')
    f.write('      auto get_modes = [&](int idx) -> std::string {\n')
    f.write('        switch (idx) {\n')
    for i in range(1, lights_amount + 1):
        f.write(f'          case {i}: return id(light_supported_modes_{i}).state;\n')
    f.write('          default: return "";\n')
    f.write('        }\n')
    f.write('      };\n')
    f.write('      return get_modes(id(current_light_index));\n')
    f.write('    on_value:\n')
    f.write('      - lambda: |-\n')
    f.write('          std::string modes = x;\n')
    f.write('          id(light_supports_color_temp) = (modes.find("color_temp") != std::string::npos);\n')
    f.write('          id(light_supports_hs) = (modes.find("hs") != std::string::npos);\n')
    f.write('          id(light_supports_rgb) = (modes.find("rgb") != std::string::npos);\n')
    f.write('          id(light_supports_brightness) = (\n')
    f.write('            modes.find("brightness") != std::string::npos ||\n')
    f.write('            id(light_supports_hs) ||\n')
    f.write('            id(light_supports_rgb) ||\n')
    f.write('            id(light_supports_color_temp)\n')
    f.write('          );\n')
    f.write('          ESP_LOGD("light_widget", "Supported modes parsed for index %d", id(current_light_index));\n')
    f.write('          if (!id(light_initial_load_complete)) {\n')
    f.write('            id(light_initial_load_complete) = true;\n')
    f.write('          }\n')
    f.write('          id(light_update_layout).execute();\n')

def main():
    try:
        subs = load_substitutions()
        lights_count = int(subs.get('lights_amount', 7))

        print(f"Generating light.yaml for {lights_count} lights...")

        with open('light_generated.yaml', 'w') as f:
            write_yaml_header(f)
            write_globals(f, lights_count)
            write_binary_sensors(f, lights_count)

            f.write('sensor:\n')
            write_brightness_sensors(f, lights_count)
            write_color_temp_sensors(f, lights_count)
            f.write('\n')

            f.write('text_sensor:\n')
            write_name_sensors(f, lights_count)
            write_hs_color_sensors(f, lights_count)
            write_supported_modes_sensors(f, lights_count)

        print(f"\nGenerated light_generated.yaml successfully!")
        print(f"\nConfiguration summary:")
        print(f"  - Lights configured: {lights_count}")
        print(f"  - Globals: {lights_count * 4 + 7 + lights_count + 5}")
        print(f"  - Binary sensors: {lights_count + 2}")
        print(f"  - Sensors: {lights_count * 2 + 2}")
        print(f"  - Text sensors: {lights_count * 3 + 2}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
