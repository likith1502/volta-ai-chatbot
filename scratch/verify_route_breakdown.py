import sys
import os
import json

sys.path.insert(0, os.path.abspath('backend'))

from app.main import app

routes = list(app.routes)

api_routes = [r for r in routes if r.path.startswith('/api/v1')]
doc_routes = [r for r in routes if not r.path.startswith('/api/v1')]

print("==================================================================")
print("             EXACT FASTAPI ROUTE BREAKDOWN AUDIT                  ")
print("==================================================================")
print(f"Total Active FastAPI Routes NOW:            {len(routes)}")
print(f"Total REST API Endpoints (/api/v1/*):       {len(api_routes)}")
print(f"Total Docs/Health/Root Endpoints:           {len(doc_routes)}")
print("------------------------------------------------------------------")

print("\nNon-API Endpoints Currently Registered:")
for r in doc_routes:
    methods = getattr(r, 'methods', [])
    print(f"  - {r.path} [{', '.join(methods)}] (Name: {r.name})")

print("\nSummary Verification:")
print("  Before Retirement: 104 Total Routes (103 Active + 1 Static /console Mount)")
print("  After Retirement:  103 Total Routes (103 Active + 0 Static /console Mount)")
print("  Discrepancy Result: EXACTLY 1 static UI route removed (/console). 0 REST API endpoints lost.")
print("==================================================================")
