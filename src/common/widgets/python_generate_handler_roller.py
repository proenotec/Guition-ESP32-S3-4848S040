# generate_handler.py
# This script auto-generates the handler from config

import yaml

# Read config
with open('python_devices_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Generate widget names list
names = [w['name'] for w in config['widgets']]

# Generate handler conditions
handler = []
for i, widget in enumerate(config['widgets']):
    handler.append({
        'if': {
            'condition': {
                'lambda': f'return x == {i};'
            },
            'then': [
                {'lvgl.page.show': widget['page']}
            ]
        }
    })

# Write devices_list.yaml
with open('devices_list.yaml', 'w') as f:
    yaml.dump(names, f, default_flow_style=False)

# Write devices_handler.yaml
with open('devices_handler.yaml', 'w') as f:
    yaml.dump(handler, f, default_flow_style=False)

print("Generated '~/bin/titov/gerardo_src/common/widgets/devices_list.yaml' and '~/bin/titov/gerardo_src/common/widgets/devices_handler.yaml' successfully!")
