#!/bin/bash
# Usage: ./test_curl.sh <key>
URL=http://localhost:5001/process

echo "--- With the given key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -H "X-API-Key: $1" -d '{"text":"hello rootsoftware"}'
echo -e "\n--- Invalid key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -H "X-API-Key: wrongkey" -d '{"text":"hello"}'
echo -e "\n--- Missing key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -d '{"text":"hello"}'
echo
