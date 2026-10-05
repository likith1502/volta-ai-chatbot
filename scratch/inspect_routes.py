import json

with open(r'C:\Users\Likit\.gemini\antigravity-ide\brain\97c6a990-3af6-4bd5-9e94-d69216e41605\scratch\api_route_inventory.json', 'r') as f:
    routes = json.load(f)

print(f"Total routes: {len(routes)}")
for r in routes:
    print(f"{r['methods']} {r['path']}")
