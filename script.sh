#!/bin/bash

# 1. On charge le fichier .env en ignorant les commentaires (#)
export $(grep -v '^#' .env | xargs)

# 2. On utilise la variable exactement comme elle est nommée dans le .env
API_KEY=$CALDERA_API_KEY
PASS=$OPENAEV_ADMIN_PASSWORD
CALDERA="http://localhost:8888"



echo "=== 1. Caldera répond-il ? ==="
curl -s -o /dev/null -w "HTTP: %{http_code}\n" "$CALDERA"

echo -e "\n=== 2. Test API v1 avec api_key dans JSON ==="
curl -s -X POST "$CALDERA/api/rest" \
  -H "Content-Type: application/json" \
  -d "{\"index\":\"abilities\",\"api_key\":\"$API_KEY\"}" | head -c 200

echo -e "\n=== 3. Test API v1 avec header Api-Key ==="
curl -s -X POST "$CALDERA/api/rest" \
  -H "Content-Type: application/json" \
  -H "Api-Key: $API_KEY" \
  -d '{"index":"abilities"}' | head -c 200

echo -e "\n=== 4. Test auth web + cookie + API v2 ==="
curl -c /tmp/cookie.txt -s -X POST "$CALDERA/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"red\",\"password\":\"$PASS\"}" > /dev/null

if [ -s /tmp/cookie.txt ]; then
    echo "Cookie obtenu"
    RESP=$(curl -b /tmp/cookie.txt -s -w "\nHTTP:%{http_code}" \
      -H "Accept: application/json" \
      "$CALDERA/api/v2/abilities")
    echo "$RESP" | head -3
else
    echo "❌ Échec obtention cookie"
fi

echo -e "\n=== 5. Logs Caldera (erreurs) ==="
docker logs openaev-lab-caldera-1 2>&1 | grep -iE "error|exception" | tail -5
