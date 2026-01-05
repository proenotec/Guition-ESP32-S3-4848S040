# python_generate_handler_buttons.py
# Smart generator that creates optimal buttonmatrix layouts based on device count

import yaml
import math

def calculate_optimal_layout(num_items):
    """
    Calculate optimal grid layout based on number of items.
    Returns (cols, rows) tuple.
    """
    if num_items <= 3:
        # For 1-3 items, use single column
        return 1, num_items
    elif num_items <= 6:
        # For 4-6 items, use 2 columns
        return 2, math.ceil(num_items / 2)
    elif num_items <= 9:
        # For 7-9 items, use 3 columns
        return 3, math.ceil(num_items / 3)
    else:
        # For 10+ items, use 3 columns (can be expanded)
        return 3, math.ceil(num_items / 3)

def chunk_list(lst, chunk_size):
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# Read config
with open('python_devices_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

widgets = config['widgets']
num_widgets = len(widgets)

# Calculate optimal layout
cols, rows = calculate_optimal_layout(num_widgets)

print(f"Generating {num_widgets} buttons in {rows}x{cols} grid layout")

# Create button data with IDs
button_data = []
for widget in widgets:
    button_data.append({
        'id': f"btn_{widget['name'].lower()}",
        'text': f"\n{widget['name']}\n",
        'page': widget['page']
    })

# Pad the last row if needed
while len(button_data) % cols != 0 and len(button_data) > cols:
    button_data.append(None)  # Empty button placeholder

# Split into rows
button_rows = chunk_list(button_data, cols)

# Generate buttonmatrix rows
matrix_rows = []
for row in button_rows:
    row_buttons = []
    for btn in row:
        if btn is None:
            # Empty button
            row_buttons.append({
                'text': '',
                'control': {'hidden': True}
            })
        else:
            row_buttons.append({
                'id': btn['id'],
                'text': btn['text']
            })
    matrix_rows.append({'buttons': row_buttons})

# Generate handler conditions for on_press
handler = []
for btn in button_data:
    if btn is not None:  # Skip empty placeholders
        handler.append({
            'if': {
                'condition': {
                    'lambda': f"return x == id({btn['id']});"
                },
                'then': [
                    {'lvgl.page.show': btn['page']}
                ]
            }
        })

# Write devices_list.yaml (button rows)
with open('devices_list.yaml', 'w') as f:
    yaml.dump(matrix_rows, f, default_flow_style=False, sort_keys=False)

# Write devices_handler.yaml (on_press handlers)
with open('devices_handler.yaml', 'w') as f:
    yaml.dump(handler, f, default_flow_style=False, sort_keys=False)

print(f"✓ Generated 'devices_list.yaml' with {cols} columns")
print(f"✓ Generated 'devices_handler.yaml' with {len(handler)} handlers")
print(f"\nLayout: {rows} rows × {cols} columns")
