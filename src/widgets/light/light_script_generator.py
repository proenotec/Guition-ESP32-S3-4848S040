#!/usr/bin/env python3
import yaml

with open('substitutions.yaml', 'r') as f:
    substitutions = yaml.safe_load(f)

lights_amount = int(substitutions['lights_amount'])

def generate_light_scripts(lights_amount):
    output = "# Auto-generated LVGL scripts based on lights_amount\n"
    output += f"# Generated for {lights_amount} lights\n\n"
    output += "script:\n"

    output += "  - id: light_switch_index\n"
    output += "    parameters:\n"
    output += "      position: int\n"
    output += "    then:\n"
    output += "      - lambda: |-\n"
    output += "          id(current_light_index) = position;\n"
    output += "          std::string entity = \"\";\n"
    output += "          switch (position) {\n"

    for i in range(1, lights_amount + 1):
        output += f"            case {i}: entity = \"${{light_entity_{i}}}\"; break;\n"

    output += "            default: entity = \"${light_entity_1}\";\n"
    output += "          }\n\n"
    output += "          id(current_light_entity) = entity;\n"
    output += "          ESP_LOGD(\"light_switch\", \"Switched to light index %d: %s\", position, entity.c_str());\n\n"
    output += "          // Copy per-light capabilities\n"
    output += "          switch (position) {\n"

    for i in range(1, lights_amount + 1):
        output += f"            case {i}:\n"
        output += f"              id(light_supports_color_temp) = id(light_{i}_supports_color_temp);\n"
        output += f"              id(light_supports_hs) = id(light_{i}_supports_hs);\n"
        output += f"              id(light_supports_rgb) = id(light_{i}_supports_rgb);\n"
        output += f"              id(light_supports_brightness) = id(light_{i}_supports_brightness);\n"
        output += f"              break;\n"

    output += "          }\n\n"
    output += "          // Force publish brightness\n"

    for i in range(1, lights_amount + 1):
        output += f"          if (position == {i} && id(light_brightness_{i}).has_state()) {{ id(light_brightness).publish_state(id(light_brightness_{i}).state); }}\n"

    output += "\n          // State\n"
    output += "          bool state_val = false;\n"
    output += "          switch (position) {\n"

    for i in range(1, lights_amount + 1):
        output += f"            case {i}: state_val = id(light_state_{i}).state; break;\n"

    output += "            default: state_val = false;\n"
    output += "          }\n\n"
    output += "          id(light_state).publish_state(state_val);\n\n"
    output += "          // Update friendly name\n"
    output += "          std::string name = \"\";\n"
    output += "          switch (position) {\n"

    for i in range(1, lights_amount + 1):
        output += f"            case {i}: name = id(light_name_{i}_stored); break;\n"

    output += "            default: name = \"Light\";\n"
    output += "          }\n\n"
    output += "          if (name.empty()) {\n"
    output += "            name = \"Undefined\";\n"
    output += "          }\n\n"
    output += "          lv_label_set_text(id(light_name_label), name.c_str());\n\n"
    output += "          // Auto-select mode\n"
    output += "          if (!(id(light_supports_color_temp) && (id(light_supports_hs) || id(light_supports_rgb)))) {\n"
    output += "            if (id(light_supports_hs) || id(light_supports_rgb)) {\n"
    output += "              id(light_is_temp_mode) = false;\n"
    output += "            } else if (id(light_supports_color_temp)) {\n"
    output += "              id(light_is_temp_mode) = true;\n"
    output += "            }\n"
    output += "          }\n\n"
    output += "          id(light_toggle_gradient).execute();\n\n"

    output += "  - id: update_home_lights_btn_color\n"
    output += "    then:\n"
    output += "      - lambda: |-\n"
    output += "          // Check if any light is on\n"
    output += "          bool any_light_on = false;\n"

    for i in range(1, lights_amount + 1):
        output += f"          if (id(light_state_{i}).state) {{ any_light_on = true; }}\n"

    output += "          ESP_LOGD(\"home_lights_btn\", \"Any light on: %d\", any_light_on);\n\n"
    output += "          // Change button shadow color\n"
    output += "          if (any_light_on) {\n"
    output += "            lv_obj_set_style_shadow_color(id(home_lights_btn), lv_color_hex(0xFF8C00), 0);\n"
    output += "            lv_obj_set_style_shadow_width(id(home_lights_btn), 12, 0);\n"
    output += "          } else {\n"
    output += "            lv_obj_set_style_shadow_color(id(home_lights_btn), lv_color_hex(0x000000), 0);\n"
    output += "            lv_obj_set_style_shadow_width(id(home_lights_btn), 8, 0);\n"
    output += "          }\n\n"
    output += "          // Find icon in hierarchy\n"
    output += "          lv_obj_t* parent = lv_obj_get_parent(id(home_lights_btn));\n"
    output += "          if (parent != nullptr) {\n"
    output += "            uint32_t parent_child_count = lv_obj_get_child_cnt(parent);\n"
    output += "            for (uint32_t i = 0; i < parent_child_count; i++) {\n"
    output += "              lv_obj_t* child = lv_obj_get_child(parent, i);\n"
    output += "              if (child != nullptr && child != id(home_lights_btn)) {\n"
    output += "                uint32_t grandchild_count = lv_obj_get_child_cnt(child);\n"
    output += "                ESP_LOGD(\"home_lights_btn\", \"Child %d has %d grandchildren\", i, grandchild_count);\n"
    output += "                for (uint32_t j = 0; j < grandchild_count; j++) {\n"
    output += "                  lv_obj_t* grandchild = lv_obj_get_child(child, j);\n"
    output += "                  if (grandchild != nullptr) {\n"
    output += "                    if (any_light_on) {\n"
    output += "                      lv_obj_set_style_text_color(grandchild, lv_color_hex(0xFFA500), 0);\n"
    output += "                    } else {\n"
    output += "                      lv_obj_set_style_text_color(grandchild, lv_color_hex(0xB0C4DE), 0);\n"
    output += "                    }\n"
    output += "                    ESP_LOGD(\"home_lights_btn\", \"Changed text color on grandchild %d of child %d\", j, i);\n"
    output += "                  }\n"
    output += "                }\n"
    output += "              }\n"
    output += "            }\n"
    output += "          }\n\n"

    output += "  - id: light_update_all_selector_icons\n"
    output += "    then:\n"
    output += "      - lambda: |-\n"
    output += "          auto get_icon_color = [](int index) -> lv_color_t {\n"
    output += "            bool is_on = false;\n"
    output += "            int brightness = 100;\n"
    output += "            float hue = 0.0f;\n"
    output += "            float sat = 0.0f;\n"
    output += "            float temp = 3000.0f;\n"
    output += "            bool has_color = false;\n"
    output += "            bool is_temp_mode_local = false;\n\n"
    output += "            // Get state for this light\n"
    output += "            switch (index) {\n"

    for i in range(1, lights_amount + 1):
        output += f"              case {i}:\n"
        output += f"                is_on = id(light_state_{i}).state;\n"
        output += f"                if (id(light_brightness_{i}).has_state() && !std::isnan(id(light_brightness_{i}).state)) {{\n"
        output += f"                  brightness = id(light_brightness_{i}).state;\n"
        output += f"                }} else {{\n"
        output += f"                  brightness = 255; // Default to full brightness if None\n"
        output += f"                }}\n"
        output += f"                break;\n"

    output += "            }\n\n"
    output += "            // If light is OFF, return gray\n"
    output += "            if (!is_on) {\n"
    output += "              return lv_color_make(153, 153, 153);\n"
    output += "            }\n\n"
    output += "            // Check if this light has color capabilities\n"
    output += "            std::string modes = \"\";\n"
    output += "            switch (index) {\n"

    for i in range(1, lights_amount + 1):
        output += f"              case {i}: modes = id(light_supported_modes_{i}).state; break;\n"

    output += "            }\n\n"
    output += "            bool supports_temp = (modes.find(\"color_temp\") != std::string::npos);\n"
    output += "            bool supports_hs = (modes.find(\"hs\") != std::string::npos);\n"
    output += "            bool supports_rgb = (modes.find(\"rgb\") != std::string::npos);\n"
    output += "            has_color = supports_temp || supports_hs || supports_rgb;\n\n"
    output += "            // If light is ON but has no color support, return yellow\n"
    output += "            if (!has_color) {\n"
    output += "              uint8_t val = 204;\n"
    output += "              if (modes.find(\"brightness\") != std::string::npos || supports_hs || supports_rgb || supports_temp) {\n"
    output += "                float bright_scale = 0.6 + (brightness / 255.0 * 0.4);\n"
    output += "                val = 255 * bright_scale;\n"
    output += "              }\n"
    output += "              return lv_color_make(val, val, 0);\n"
    output += "            }\n\n"
    output += "            // Get color data for this light\n"
    output += "            std::string hs_str = \"\";\n"
    output += "            switch (index) {\n"

    for i in range(1, lights_amount + 1):
        output += f"              case {i}: hs_str = id(light_hs_color_{i}).state; break;\n"

    output += "            }\n\n"
    output += "            // Parse HS if available\n"
    output += "            if (!hs_str.empty() && hs_str != \"None\" && (supports_hs || supports_rgb)) {\n"
    output += "              size_t start = hs_str.find('(') + 1;\n"
    output += "              size_t comma = hs_str.find(',');\n"
    output += "              size_t end = hs_str.find(')');\n"
    output += "              if (start < comma && comma < end) {\n"
    output += "                hue = atof(hs_str.substr(start, comma - start).c_str());\n"
    output += "                sat = atof(hs_str.substr(comma + 1, end - comma - 1).c_str());\n"
    output += "                is_temp_mode_local = false;\n"
    output += "              }\n"
    output += "            } else if (supports_temp) {\n"
    output += "              switch (index) {\n"

    for i in range(1, lights_amount + 1):
        output += f"                case {i}:\n"
        output += f"                  if (id(light_color_temp_{i}).has_state() && !std::isnan(id(light_color_temp_{i}).state)) {{\n"
        output += f"                    temp = id(light_color_temp_{i}).state;\n"
        output += f"                  }}\n"
        output += f"                  break;\n"

    output += "              }\n"
    output += "              is_temp_mode_local = true;\n"
    output += "            }\n\n"
    output += "            // Calculate RGB color\n"
    output += "            uint8_t r = 255, g = 255, b = 255;\n"
    output += "            if (is_temp_mode_local) {\n"
    output += "              // Kelvin to RGB\n"
    output += "              float t = temp / 100.0f;\n"
    output += "              float r_val = 0.0f, g_val = 0.0f, b_val = 0.0f;\n"
    output += "              if (t <= 66.0f) {\n"
    output += "                r_val = 255.0f;\n"
    output += "                g_val = 99.4708025861f * log(t) - 161.1195681661f;\n"
    output += "                if (t <= 19.0f) b_val = 0.0f;\n"
    output += "                else b_val = 138.5177312231f * log(t - 10.0f) - 305.0447927307f;\n"
    output += "              } else {\n"
    output += "                r_val = 329.698727446f * pow(t - 60.0f, -0.1332047592f);\n"
    output += "                g_val = 288.1221695283f * pow(t - 60.0f, -0.0755148492f);\n"
    output += "                b_val = 255.0f;\n"
    output += "              }\n"
    output += "              r = (uint8_t)fminf(fmaxf(r_val, 0.0f), 255.0f);\n"
    output += "              g = (uint8_t)fminf(fmaxf(g_val, 0.0f), 255.0f);\n"
    output += "              b = (uint8_t)fminf(fmaxf(b_val, 0.0f), 255.0f);\n"
    output += "            } else {\n"
    output += "              // HS to RGB\n"
    output += "              uint16_t h = (uint16_t)fminf(fmaxf(hue, 0.0f), 359.0f);\n"
    output += "              uint8_t s = (uint8_t)fminf(fmaxf(sat, 0.0f), 100.0f);\n"
    output += "              lv_color_t full = lv_color_hsv_to_rgb(h, s, 100);\n"
    output += "              lv_color32_t full32;\n"
    output += "              full32.full = lv_color_to32(full);\n"
    output += "              r = full32.ch.red;\n"
    output += "              g = full32.ch.green;\n"
    output += "              b = full32.ch.blue;\n"
    output += "            }\n\n"
    output += "            // Apply brightness scaling (60% to 100%)\n"
    output += "            float bright_scale = 0.6 + (brightness / 255.0 * 0.4);\n"
    output += "            r = r * bright_scale;\n"
    output += "            g = g * bright_scale;\n"
    output += "            b = b * bright_scale;\n"
    output += "            return lv_color_make(r, g, b);\n"
    output += "          };\n\n"
    output += "          // Update all selector icons\n"

    for i in range(1, lights_amount + 1):
        output += f"          lv_obj_set_style_text_color(id(light_icon_{i}), get_icon_color({i}), 0);\n"

    return output

lvgl_output = generate_light_scripts(lights_amount)

with open('light_scripts.yaml', 'w') as f:
    f.write(lvgl_output)

print(f"Generated light_scripts.yaml for {lights_amount} lights")
