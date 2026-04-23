import requests, json

print("🔍 Téléchargement du Swagger OpenAEV...")
try:
    resp = requests.get("http://localhost:8090/v3/api-docs")
    if resp.status_code == 200:
        data = resp.json()
        print("✅ Swagger récupéré. Analyse des routes...\n")
        
        for path, methods in data.get("paths", {}).items():
            if "expectations" in path:
                print(f"🎯 Route : {path}")
                for method, details in methods.items():
                    if method in ["put", "post", "patch"]:
                        try:
                            schema_ref = details["requestBody"]["content"]["application/json"]["schema"]["$ref"]
                            model_name = schema_ref.split("/")[-1]
                            schema = data["components"]["schemas"].get(model_name, {})
                            print(f"   👉 [{method.upper()}] Body exigé ({model_name}) :")
                            for prop_name, prop_details in schema.get("properties", {}).items():
                                prop_type = prop_details.get("type", "unknown")
                                print(f"      - {prop_name} ({prop_type})")
                        except Exception:
                            print(f"   👉 [{method.upper()}] (Modèle complexe ou Body vide)")
                print("-" * 50)
    else:
        print(f"❌ Erreur API: {resp.status_code}")
except Exception as e:
    print(f"Erreur de connexion : {e}")
