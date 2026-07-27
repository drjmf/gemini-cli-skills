import binascii
import json
import subprocess
import sys
import os

def run_mysql(sql):
    cmd = ["docker", "exec", "-i", "ragflow-mysql-1", "mysql", "-u", "root", "-p88julia88"]
    result = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if result.returncode != 0:
        return None, result.stderr
    return result.stdout, None

def get_agent_dsl_hex(agent_id):
    sql = f"USE rag_flow; SELECT HEX(dsl) FROM user_canvas WHERE id = '{agent_id}';"
    stdout, stderr = run_mysql(sql)
    if not stdout:
        return None, stderr
    lines = stdout.strip().split('\n')
    if len(lines) < 2:
        return None, "No data found"
    return lines[1].strip(), None

def update_agent_dsl_hex(agent_id, dsl_dict):
    new_json = json.dumps(dsl_dict)
    new_hex = binascii.hexlify(new_json.encode('utf-8')).decode('ascii')
    sql = f"USE rag_flow; UPDATE user_canvas SET dsl = UNHEX('{new_hex}') WHERE id = '{agent_id}';"
    stdout, stderr = run_mysql(sql)
    if stderr:
        return False, stderr
    return True, None

def get_backup_dsl_hex(agent_id):
    sql = f"USE rag_flow; SELECT HEX(dsl) FROM user_canvas_version WHERE user_canvas_id = '{agent_id}' ORDER BY create_time DESC LIMIT 1;"
    stdout, stderr = run_mysql(sql)
    if not stdout:
        return None, stderr
    lines = stdout.strip().split('\n')
    if len(lines) < 2:
        return None, "No backup found"
    return lines[1].strip(), None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 repair.py <agent_id> <action> [params]")
        print("Actions: get, update, restore, list-agents")
        sys.exit(1)

    agent_id = sys.argv[1]
    action = sys.argv[2]

    if action == "list-agents":
        sql = "USE rag_flow; SELECT id, title, `release` FROM user_canvas WHERE title LIKE '%" + agent_id + "%';"
        stdout, stderr = run_mysql(sql)
        print(stdout if stdout else stderr)
    
    elif action == "get":
        hex_data, err = get_agent_dsl_hex(agent_id)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print(hex_data)

    elif action == "restore":
        hex_data, err = get_backup_dsl_hex(agent_id)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        sql = f"USE rag_flow; UPDATE user_canvas SET dsl = UNHEX('{hex_data}') WHERE id = '{agent_id}';"
        _, err = run_mysql(sql)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print("Agent restored from version history successfully.")

    elif action == "update":
        if len(sys.argv) < 4:
            print("Error: JSON file path required for update")
            sys.exit(1)
        json_file = sys.argv[3]
        with open(json_file, 'r') as f:
            dsl = json.load(f)
        success, err = update_agent_dsl_hex(agent_id, dsl)
        if not success:
            print(f"Error: {err}")
            sys.exit(1)
        print("Agent updated successfully via HEX injection.")

if __name__ == "__main__":
    main()
