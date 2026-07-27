import sys
import json
import subprocess
import os
import re

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return None, result.stderr
        return result.stdout, None
    except Exception as e:
        return None, str(e)

def get_agent_dsl(agent_id, mysql_pwd):
    cmd = f"docker exec ragflow-mysql-1 mysql -u root -p{mysql_pwd} -e \"USE rag_flow; SELECT name, canvas FROM agent WHERE id = '{agent_id}' \G\""
    # Fallback to user_canvas if agent table doesn't exist
    stdout, _ = run_command(cmd)
    if not stdout or "ERROR 1146" in stdout:
        cmd = f"docker exec ragflow-mysql-1 mysql -u root -p{mysql_pwd} -e \"USE rag_flow; SELECT title as name, dsl as canvas FROM user_canvas WHERE id = '{agent_id}' \G\""
        stdout, _ = run_command(cmd)
    
    if not stdout:
        return None
    
    name_match = re.search(r"name: (.*)", stdout)
    canvas_match = re.search(r"canvas: (\{.*\})", stdout, re.DOTALL)
    
    if name_match and canvas_match:
        return {
            "name": name_match.group(1).strip(),
            "dsl": json.loads(canvas_match.group(1).strip())
        }
    return None

def get_kb_names(kb_ids, mysql_pwd):
    if not kb_ids:
        return {}
    ids_str = "','".join(kb_ids)
    cmd = f"docker exec ragflow-mysql-1 mysql -u root -p{mysql_pwd} -e \"USE rag_flow; SELECT id, name FROM knowledgebase WHERE id IN ('{ids_str}');\""
    stdout, _ = run_command(cmd)
    if not stdout:
        return {}
    
    mapping = {}
    lines = stdout.strip().split('\n')[1:] # Skip header
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 2:
            mapping[parts[0].strip()] = parts[1].strip()
    return mapping

def parse_logs(agent_id, tail=500):
    cmd = f"docker logs --tail {tail} ragflow-ragflow-cpu-1"
    stdout, _ = run_command(cmd)
    if not stdout:
        return []
    
    # Simple regex to find log blocks for the agent
    # In real logs, we look for "INFO [37]" or specific request patterns
    # For this script, we'll return the raw tail for the agent to process
    return stdout

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 report.py <agent_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    mysql_pwd = os.environ.get("MYSQL_PASSWORD", "88julia88")
    
    agent_info = get_agent_dsl(agent_id, mysql_pwd)
    if not agent_info:
        print(f"Agent {agent_id} not found.")
        sys.exit(1)
    
    print(f"Report for Agent: {agent_info['name']} ({agent_id})")
    print("-" * 40)
    
    # Map Tools to Datasets
    tools = []
    try:
        # Check standard Agent component
        components = agent_info['dsl'].get('components', {})
        for cid, comp in components.items():
            if comp.get('obj', {}).get('component_name') == 'Agent':
                tools = comp['obj']['params'].get('tools', [])
                break
    except:
        pass

    if tools:
        print("\nTool to Dataset Mapping:")
        all_kb_ids = []
        for t in tools:
            all_kb_ids.extend(t.get('params', {}).get('dataset_ids', []))
        
        kb_mapping = get_kb_names(list(set(all_kb_ids)), mysql_pwd)
        
        for i, t in enumerate(tools):
            alias = t.get('name', 'Unknown')
            kb_ids = t.get('params', {}).get('dataset_ids', [])
            names = [kb_mapping.get(kid, kid) for kid in kb_ids]
            print(f"search_my_dateset_{i} | {alias} | {', '.join(names)}")
    
    print("\nRecent Logs (Tail 100):")
    logs = parse_logs(agent_id, 100)
    print(logs)

if __name__ == "__main__":
    main()
