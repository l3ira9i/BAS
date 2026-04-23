import requests
import json
import time

KIBANA = "http://localhost:5601"
HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}
TTPs = ["T1082", "T1059", "T1083", "T1003", "T1071", "T1057"]

print("🔍 Récupération des règles depuis Kibana...")
resp = requests.get(f"{KIBANA}/api/detection_engine/rules/_find?per_page=2000", headers=HEADERS)

if resp.status_code != 200:
    print(f"❌ Erreur API: {resp.text}")
    exit()

rules = resp.json().get("data", [])
print(f"📦 {len(rules)} règles trouvées au total dans la base.")

ids_to_enable = []
already_enabled = 0

for r in rules:
    rule_text = json.dumps(r).upper()
    has_ttp = any(ttp in rule_text for ttp in TTPs)

    if has_ttp:
        if not r.get("enabled", False):
            ids_to_enable.append(r.get("id"))
        else:
            already_enabled += 1

print(f"ℹ️ {already_enabled} règles étaient déjà actives.")
print(f"🎯 {len(ids_to_enable)} règles prêtes à être activées.")

if ids_to_enable:
    print("🚀 Activation en cours (découpage par lots de 100)...")
    batch_size = 100
    success_count = 0
    
    # On boucle sur la liste par pas de 100
    for i in range(0, len(ids_to_enable), batch_size):
        batch = ids_to_enable[i:i + batch_size]
        payload = {"action": "enable", "ids": batch}
        
        bulk_resp = requests.post(f"{KIBANA}/api/detection_engine/rules/_bulk_action", headers=HEADERS, json=payload)
        
        if bulk_resp.status_code == 200:
            success_count += len(batch)
            print(f"  ✅ Lot de {len(batch)} règles activé avec succès.")
        else:
            print(f"  ❌ Erreur pour un lot : {bulk_resp.text}")
        
        # Petite pause pour ne pas brusquer Kibana
        time.sleep(1)

    print(f"🎉 Opération terminée ! {success_count} règles activées.")
