import json
import uuid
import sys
import os

def hex_to_json(hex_data):
    return json.loads(bytes.fromhex(hex_data).decode('utf-8'))

def json_to_hex(data):
    return json.dumps(data).encode('utf-8').hex()

def clone_node(source_hex, target_hex, node_name):
    source = hex_to_json(source_hex)
    target = hex_to_json(target_hex)
    
    # 1. Find node in source components
    source_cid = None
    for cid, cobj in source.get('components', {}).items():
        if cobj.get('obj', {}).get('name') == node_name:
            source_cid = cid
            break
            
    if not source_cid:
        # Try finding by ID if name match fails
        if node_name in source.get('components', {}):
            source_cid = node_name
        else:
            print(f'Error: Node \"{node_name}\" not found in source agent.')
            return None

    # 2. Extract component logic
    component = source['components'][source_cid]
    
    # 3. Create unique ID and set name
    type_prefix = source_cid.split(':')[0] if ':' in source_cid else 'Node'
    new_cid = f'{type_prefix}:{str(uuid.uuid4().hex)[:12]}'
    component['obj']['name'] = node_name
    component['upstream'] = []
    component['downstream'] = []
    
    # 4. Find visual graph node
    source_graph_node = None
    for node in source.get('graph', {}).get('nodes', []):
        if node.get('id') == source_cid:
            source_graph_node = node
            break
            
    if not source_graph_node:
        # Create a default graph node if not found
        source_graph_node = {
            "id": new_cid,
            "type": f"{type_prefix.lower()}Node",
            "data": {
                "label": type_prefix,
                "name": node_name,
                "form": component['obj'].get('params', {})
            },
            "position": {"x": 0, "y": 0}
        }
    else:
        source_graph_node = json.loads(json.dumps(source_graph_node)) # deep copy
        source_graph_node['id'] = new_cid
        source_graph_node['data']['name'] = node_name
        # Adjust position slightly to avoid exact overlap if target has similar layout
        source_graph_node['position']['x'] += 50
        source_graph_node['position']['y'] += 50

    # 5. Inject into target
    if 'components' not in target: target['components'] = {}
    target['components'][new_cid] = component
    
    if 'graph' not in target: target['graph'] = {"nodes": [], "edges": []}
    target['graph']['nodes'].append(source_graph_node)
    
    # Top-level nodes for some UI versions
    if 'nodes' not in target: target['nodes'] = []
    target['nodes'].append({'id': new_cid, 'obj': component['obj'], 'type': source_graph_node['type']})

    return json.dumps(target)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 clone.py <source_hex> <target_hex> <node_name>')
        sys.exit(1)
        
    res = clone_node(sys.argv[1], sys.argv[2], sys.argv[3])
    if res:
        print(res)
