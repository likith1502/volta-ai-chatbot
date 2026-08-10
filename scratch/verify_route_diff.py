import sys
import os
import json

sys.path.insert(0, os.path.abspath('backend'))

from app.main import app

routes_now = set(r.path for r in app.routes)

prev_path = r'C:\Users\Likit\.gemini\antigravity-ide\brain\97c6a990-3af6-4bd5-9e94-d69216e41605\scratch\api_route_inventory.json'
with open(prev_path, 'r') as f:
    prev_inventory = json.load(f)

prev_routes = set(r['path'] for r in prev_inventory)

print(f"Total Routes BEFORE (/console included): {len(prev_routes)}")
print(f"Total Routes NOW (/console unmounted):   {len(routes_now)}")

missing = prev_routes - routes_now
added = routes_now - prev_routes

print("\n--- DIFFERENCE ANALYSIS ---")
print(f"Removed Routes: {missing}")
print(f"Added Routes:   {added}")

api_prev = set(r for r in prev_routes if r.startswith('/api/'))
api_now = set(r for r in routes_now if r.startswith('/api/'))

print(f"\nREST API Routes (/api/v1/*) BEFORE: {len(api_prev)}")
print(f"REST API Routes (/api/v1/*) NOW:    {len(api_now)}")
print(f"REST API Routes Missing:             {api_prev - api_now}")

non_api_prev = prev_routes - api_prev
non_api_now = routes_now - api_now

print(f"\nNon-API Routes (Docs, Root, Static) BEFORE: {non_api_prev}")
print(f"Non-API Routes (Docs, Root, Static) NOW:    {non_api_now}")
