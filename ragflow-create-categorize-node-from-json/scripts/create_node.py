import json
import uuid
import sys
import os

def hex_to_json(hex_data):
    return json.loads(bytes.fromhex(hex_data).decode('utf-8'))

def create_categorize_node(agent_dsl_hex, json_path, node_name, position_x=-700, position_y=300):
    # 1. Load data
    target_data = hex_to_json(agent_dsl_hex)
    with open(json_path, 'r') as f:
        source_data = json.load(f)

    # 2. Prepare update map from JSON
    new_categories_map = {}
    for cat in source_data:
        cat_name = cat.get('category') or cat.get('name')
        cat_desc = cat.get('description') or f"Questions related to {cat_name.replace('_', ' ')}"
        examples_raw = cat.get('examples', [])
        
        if isinstance(examples_raw, str):
            example_lines = [line.strip() for line in examples_raw.split('\n') if line.strip()]
        else:
            example_lines = [str(ex).strip() for ex in examples_raw if str(ex).strip()]
            
        new_categories_map[cat_name] = {
            "description": cat_desc,
            "examples": example_lines,
            "ui_examples": [{"value": ex} for ex in example_lines]
        }

    # 3. Determine if we are updating an existing node
    existing_cid = None
    existing_pos = {"x": position_x, "y": position_y}
    
    for cid, cobj in target_data.get('components', {}).items():
        if cobj.get('obj', {}).get('name') == node_name:
            existing_cid = cid
            break
            
    if not existing_cid:
        for node in target_data.get('graph', {}).get('nodes', []):
            if node.get('data', {}).get('name') == node_name:
                existing_cid = node['id']
                existing_pos = node['position']
                break

    # 4. Process Logic and Items
    if existing_cid and existing_cid in target_data['components']:
        new_cid = existing_cid
        params = target_data['components'][new_cid]['obj']['params']
        
        # A) Update 'category_description' map (LLM Logic)
        if 'category_description' not in params: params['category_description'] = {}
        for name, data in new_categories_map.items():
            if name not in params['category_description']:
                params['category_description'][name] = {"to": []}
            params['category_description'][name]['description'] = data['description']
            params['category_description'][name]['examples'] = data['examples']

        # B) Update 'items' list (UI Editor)
        if 'items' not in params: params['items'] = []
        for name, data in new_categories_map.items():
            found = False
            for i, it in enumerate(params['items']):
                if it['name'] == name:
                    params['items'][i]['description'] = data['description']
                    params['items'][i]['examples'] = data['ui_examples']
                    found = True
                    break
            if not found:
                params['items'].append({
                    "description": data['description'],
                    "examples": data['ui_examples'],
                    "name": name,
                    "uuid": str(uuid.uuid4())
                })
        params['name'] = node_name
    else:
        # Fresh node creation
        new_cid = f"Categorize:{str(uuid.uuid4().hex)[:12]}"
        items = []
        category_description = {}
        for name, data in new_categories_map.items():
            items.append({
                "description": data['description'],
                "examples": data['ui_examples'],
                "name": name,
                "uuid": str(uuid.uuid4())
            })
            category_description[name] = {
                "description": data['description'],
                "examples": data['examples'],
                "to": []
            }
            
        params = {
            "frequencyPenaltyEnabled": True,
            "frequency_penalty": 0.7,
            "items": items,
            "llm_id": "deepseek/deepseek-v4-flash@Deepseek@OpenAI-API-Compatible",
            "maxTokensEnabled": False,
            "max_tokens": 256,
            "message_history_window_size": 1,
            "outputs": {"category_name": {"type": "string"}},
            "parameter": "Precise",
            "presencePenaltyEnabled": True,
            "presence_penalty": 0.4,
            "query": "sys.query",
            "temperature": 0.1,
            "temperatureEnabled": True,
            "topPEnabled": True,
            "top_p": 0.3,
            "category_description": category_description,
            "name": node_name
        }

    component = {
        "obj": {
            "component_name": "Categorize",
            "name": node_name,
            "params": params
        },
        "upstream": target_data['components'][new_cid]['upstream'] if existing_cid else [],
        "downstream": target_data['components'][new_cid]['downstream'] if existing_cid else []
    }

    # 5. Inject into DSL
    target_data['components'][new_cid] = component

    # Sync visual graph node
    node_found = False
    for i, node in enumerate(target_data['graph']['nodes']):
        if node['id'] == new_cid:
            target_data['graph']['nodes'][i]['data']['form'] = params
            target_data['graph']['nodes'][i]['data']['name'] = node_name
            node_found = True
            break
            
    if not node_found:
        target_data['graph']['nodes'].append({
            "id": new_cid,
            "type": "categorizeNode",
            "data": {
                "label": "Categorize",
                "name": node_name,
                "form": params
            },
            "position": existing_pos,
            "selected": True,
            "sourcePosition": "right",
            "targetPosition": "left"
        })

    # Sync top-level nodes list
    if 'nodes' not in target_data: target_data['nodes'] = []
    top_node_found = False
    for i, node in enumerate(target_data['nodes']):
        if node['id'] == new_cid:
            target_data['nodes'][i]['obj'] = component["obj"]
            top_node_found = True
            break
    if not top_node_found:
        target_data['nodes'].append({
            "id": new_cid,
            "obj": component["obj"],
            "type": "categorizeNode"
        })

    return json.dumps(target_data)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 create_node.py <dsl_hex> <json_path> <node_name> [pos_x] [pos_y]')
        sys.exit(1)
    
    px = int(sys.argv[4]) if len(sys.argv) > 4 else -700
    py = int(sys.argv[5]) if len(sys.argv) > 5 else 300
    
    print(create_categorize_node(sys.argv[1], sys.argv[2], sys.argv[3], px, py))
