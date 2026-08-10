import json
import re
import os

with open(r'C:\Users\Likit\.gemini\antigravity-ide\brain\97c6a990-3af6-4bd5-9e94-d69216e41605\scratch\api_route_inventory.json', 'r') as f:
    routes = json.load(f)

verified_paths = {r['path']: [m.upper() for m in r['methods']] for r in routes}

api_dir = r'c:\Users\Likit\Desktop\Volta-AI-Chatbot\frontend\src\api'
api_files = [f for f in os.listdir(api_dir) if f.endswith('.ts') and f != 'client.ts']

audit = []

for af in api_files:
    file_path = os.path.join(api_dir, af)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matches = re.findall(r"apiClient\.(get|post|put|patch|delete)\(['\"]([^'\"]+)['\"]", content)
    for method, path in matches:
        full_path = '/api/v1' + path
        if full_path in verified_paths:
            allowed = verified_paths[full_path]
            if method.upper() in allowed:
                status = 'VERIFIED'
            else:
                status = f'MISMATCHED (HTTP Method {method.upper()} vs {allowed})'
        else:
            status = 'UNAVAILABLE'
        audit.append({
            'file': af,
            'method': method.upper(),
            'path': path,
            'full_path': full_path,
            'status': status
        })

print(json.dumps(audit, indent=2))
