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

    # 2. Prepare categories
    items = []
    category_description = {}
    for cat in source_data:
        # Support both 'category' and 'name' keys in JSON
        cat_name = cat.get('category') or cat.get('name')
        examples_raw = cat.get('examples', [])
        
        if isinstance(examples_raw, str):
            example_lines = [line.strip() for line in examples_raw.split('\n') if line.strip()]
        else:
            example_lines = [str(ex).strip() for ex in examples_raw if str(ex).strip()]
            
        items.append({
            "description": f"Questions related to {cat_name.replace('_', ' ')}",
            "examples": [{"value": ex} for ex in example_lines],
            "name": cat_name,
            "uuid": str(uuid.uuid4())
        })
        category_description[cat_name] = {
            "description": f"Questions related to {cat_name.replace('_', ' ')}",
            "examples": example_lines,
            "to": []
        }

    # 3. Create unique ID and Component
    new_cid = f"Categorize:{str(uuid.uuid4().hex)[:12]}"
    
    # Use a default LLM/Params structure
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
        "upstream": [],
        "downstream": []
    }

    # 4. Inject into DSL
    if 'components' not in target_data: target_data['components'] = {}
    target_data['components'][new_cid] = component

    if 'graph' not in target_data: target_data['graph'] = {"nodes": [], "edges": []}
    target_data['graph']['nodes'].append({
        "id": new_cid,
        "type": "categorizeNode",
        "data": {
            "label": "Categorize",
            "name": node_name,
            "form": params
        },
        "position": {"x": position_x, "y": position_y},
        "selected": True,
        "sourcePosition": "right",
        "targetPosition": "left"
    })

    if 'nodes' not in target_data: target_data['nodes'] = []
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
