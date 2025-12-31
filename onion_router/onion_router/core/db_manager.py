import json
import os

DB_FILE = "nodes.json"

def save_node_to_db(name, ip, port, pub_key):
    data = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {}
    
    data[name] = {'ip': ip, 'port': int(port), 'key': pub_key}
    
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_nodes_from_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}
