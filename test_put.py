import os, requests, json

# Récupération du Token depuis le .env
TOKEN = os.popen("grep OPENAEV_ADMIN_TOKEN ~/bas-lab/docker/.env | cut -d= -f2").read().strip()
URL = "http://localhost:8090/api/injects/expectations"
HEADERS = {"Authorization": f"Bearer " + TOKEN, "Content-Type": "application/json"}

# 1. On télécharge tout
print("1️⃣ Récupération des attentes...")
resp = requests.get(URL, headers=HEADERS)
expectations = resp.json()

pending_exps = [e for e in expectations if e.get("inject_expectation_status") == "PENDING"]

if not pending_exps:
    print("❌ Aucune attente PENDING trouvée. Lance une attaque dans OpenAEV d'abord !")
    exit()

exp = pending_exps[0]
exp_id = exp["inject_expectation_id"]
print(f"🎯 Attente trouvée : {exp_id}")

# 2. On modifie les champs sur l'objet COMPLET
exp["inject_expectation_score"] = 100
# Ajout de la trace du SIEM dans le tableau des résultats (comme vu dans ton GET)
exp["inject_expectation_results"].append({
    "result_score": 100,
    "source_type": "security-platform",
    "source_platform": "SIEM",
    "source_name": "Test Python (GET-Modify-PUT)"
})

# 3. On renvoie l'objet entier !
print("2️⃣ Envoi de l'objet complet mis à jour...")
put_url = f"{URL}/{exp_id}"
put_resp = requests.put(put_url, headers=HEADERS, json=exp)

print(f"\n🚀 Résultat du serveur : {put_resp.status_code}")
if put_resp.status_code == 200:
    print("✅ SUCCÈS TOTAL ! C'était bien ça le secret !")
else:
    print(f"❌ Échec : {put_resp.text}")
