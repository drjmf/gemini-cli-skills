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

    # 2. Prepare new categories from JSON
    new_items_list = []
    new_category_description = {}
    for cat in source_data:
        cat_name = cat.get('category') or cat.get('name')
        cat_desc = cat.get('description') or f"Questions related to {cat_name.replace('_', ' ')}"
        examples_raw = cat.get('examples', [])
        
        if isinstance(examples_raw, str):
            example_lines = [line.strip() for line in examples_raw.split('\n') if line.strip()]
        else:
            example_lines = [str(ex).strip() for ex in examples_raw if str(ex).strip()]
            
        new_items_list.append({
            "description": cat_desc,
            "examples": [{"value": ex} for ex in example_lines],
            "name": cat_name,
            "uuid": str(uuid.uuid4())
        })
        new_category_description[cat_name] = {
            "description": cat_desc,
            "examples": example_lines,
            "to": []
        }

    # 3. Determine if we are updating an existing node or creating a new one
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

    # 4. If updating, merge with existing items
    if existing_cid and existing_cid in target_data['components']:
        existing_comp = target_data['components'][existing_cid]
        existing_params = existing_comp['obj']['params']
        
        # Merge items
        merged_items = existing_params.get('items', [])
        if not merged_items:
             # Try getting from graph node if logic list is empty
             for n in target_data.get('graph', {}).get('nodes', []):
                 if n['id'] == existing_cid:
                     merged_items = n.get('data', {}).get('form', {}).get('items', [])
                     break
        
        existing_names = {it['name'] for it in merged_items}
        
        # Update existing items with new data, or add new ones
        for new_it in new_items_list:
            found = False
            for i, it in enumerate(merged_items):
                if it['name'] == new_it['name']:
                    merged_items[i]['description'] = new_it['description']
                    merged_items[i]['examples'] = new_it['examples']
                    found = True
                    break
            if not found:
                merged_items.append(new_it)
        
        # Merge descriptions
        merged_desc = existing_params.get('category_description', {})
        merged_desc.update(new_category_description)
        
        params = existing_params.copy()
        params['items'] = merged_items
        params['category_description'] = merged_desc
        params['name'] = node_name
        
        new_cid = existing_cid
    else:
        # Fresh node creation
        new_cid = f"Categorize:{str(uuid.uuid4().hex)[:12]}"
        params = {
            "frequencyPenaltyEnabled": True,
            "frequency_penalty": 0.7,
            "items": new_items_list,
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
            "category_description": new_category_description,
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

    # Update or add visual graph node
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

    # Update or add top-level nodes list
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
