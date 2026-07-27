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
    # Try user_canvas first as it's common for custom agents
    cmd = f"docker exec ragflow-mysql-1 mysql -u root -p{mysql_pwd} -e \"USE rag_flow; SELECT title as name, dsl as canvas FROM user_canvas WHERE id = '{agent_id}' \G\""
    stdout, _ = run_command(cmd)
    
    if not stdout or "ERROR" in stdout:
        # Fallback to agent table
        cmd = f"docker exec ragflow-mysql-1 mysql -u root -p{mysql_pwd} -e \"USE rag_flow; SELECT name, canvas FROM agent WHERE id = '{agent_id}' \G\""
        stdout, _ = run_command(cmd)
    
    if not stdout:
        return None
    
    name_match = re.search(r"name: (.*)", stdout)
    canvas_match = re.search(r"canvas: (\{.*\})", stdout, re.DOTALL)
    
    if name_match and canvas_match:
        try:
            return {
                "name": name_match.group(1).strip(),
                "dsl": json.loads(canvas_match.group(1).strip())
            }
        except:
            pass
    return None

def analyze_performance(agent_info):
    report = []
    dsl = agent_info['dsl']
    components = dsl.get('components', {})
    
    # 1. Check for TOC Enhancement
    toc_tools = []
    for cid, comp in components.items():
        if comp.get('obj', {}).get('component_name') == 'Agent':
            tools = comp['obj']['params'].get('tools', [])
            for t in tools:
                if t.get('params', {}).get('toc_enhance'):
                    toc_tools.append(t.get('name', t.get('id')))
    
    if toc_tools:
        report.append(f"[CRITICAL] TOC Enhancement enabled on: {', '.join(toc_tools)}")
        report.append("  - Impact: Can inject 1M+ tokens of table-of-contents data into LLM context.")
        report.append("  - Recommendation: Disable TOC Enhancement for these tools unless strictly necessary.")

    # 2. Check for Top_K values
    high_k_tools = []
    for cid, comp in components.items():
        if comp.get('obj', {}).get('component_name') == 'Agent':
            tools = comp['obj']['params'].get('tools', [])
            for t in tools:
                top_k = t.get('params', {}).get('top_k', 0)
                if top_k > 512:
                    high_k_tools.append(f"{t.get('name')} (k={top_k})")
    
    if high_k_tools:
        report.append(f"[WARNING] High Top_K detected on: {', '.join(high_k_tools)}")
        report.append("  - Impact: Large vector search space might slow down retrieval.")
        report.append("  - Recommendation: If not using a Reranker, reduce Top_K to < 100.")

    # 3. Check for Reranker usage
    missing_rerank = []
    for cid, comp in components.items():
        if comp.get('obj', {}).get('component_name') == 'Agent':
            tools = comp['obj']['params'].get('tools', [])
            for t in tools:
                if not t.get('params', {}).get('rerank_id'):
                    missing_rerank.append(t.get('name'))
    
    if missing_rerank:
        report.append(f"[INFO] No Reranker configured for: {', '.join(missing_rerank)}")
        report.append("  - Impact: Retrieval quality depends solely on vector similarity.")
        report.append("  - Recommendation: Enable a Reranker (e.g. bge-reranker) to improve quality without TOC overhead.")

    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <agent_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    mysql_pwd = os.environ.get("MYSQL_PASSWORD", "88julia88")
    
    agent_info = get_agent_dsl(agent_id, mysql_pwd)
    if not agent_info:
        print(f"Error: Agent {agent_id} not found in database.")
        sys.exit(1)
    
    print(f"Performance Analysis for: {agent_info['name']} ({agent_id})")
    print("-" * 50)
    
    findings = analyze_performance(agent_info)
    if not findings:
        print("No immediate performance bottlenecks found in DSL configuration.")
    else:
        for line in findings:
            print(line)

if __name__ == "__main__":
    main()
