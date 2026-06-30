import os
from supabase import create_client

url = "https://ixkmbmequacygqodlugu.supabase.co"
anon_key = "sb_publishable_hzpmaggMDqtqbRaPaRz0dA_hSgWcIwu"

client = create_client(url, anon_key)

try:
    res = client.table("knowledge_items").select("module,question").execute()
    data = res.data or []
    print(f"Total rows fetched via Anon Key: {len(data)}")
    
    modules = {}
    for r in data:
        m = r["module"]
        modules[m] = modules.get(m, 0) + 1
    
    print("\nBreakdown by module:")
    for m, c in modules.items():
        print(f"  - {m}: {c} rows")
        
    print("\nSample questions:")
    for r in data[:10]:
        print(f"  [{r['module']}] {r['question']}")
        
except Exception as e:
    print(f"Error fetching: {e}")
