#!/bin/bash
# Requires jq (or copy the tokens manually from the login responses).
URL=http://localhost:5002
J='Content-Type: application/json'

echo "1) Invalid credentials -> 401 (authentication fails)"
curl -s -i -X POST $URL/login -H "$J" -d '{"username":"bob","password":"wrong"}' | head -1

ADMIN=$(curl -s -X POST $URL/login -H "$J" -d '{"username":"alice","password":"admin123"}' | jq -r .token)
EMP=$(curl -s -X POST $URL/login -H "$J" -d '{"username":"bob","password":"emp123"}' | jq -r .token)

echo -e "\n2) No token -> 401"
curl -s -i $URL/employees | head -1

echo -e "\n3) Employee views records -> 200"
curl -s $URL/employees -H "Authorization: Bearer $EMP"

echo -e "\n\n4) Employee tries to add (authenticated but NOT authorized) -> 403"
curl -s -i -X POST $URL/employees -H "$J" -H "Authorization: Bearer $EMP" -d '{"name":"X","position":"Y","salary":1}' | head -1

echo -e "\n5) Admin adds -> 201"
curl -s -X POST $URL/employees -H "$J" -H "Authorization: Bearer $ADMIN" -d '{"name":"Zain","position":"QA","salary":60000}'

echo -e "\n\n6) Admin updates -> 200"
curl -s -X PUT $URL/employees/1 -H "$J" -H "Authorization: Bearer $ADMIN" -d '{"salary":90000}'

echo -e "\n\n7) Employee tries to delete -> 403"
curl -s -i -X DELETE $URL/employees/1 -H "Authorization: Bearer $EMP" | head -1

echo -e "\n8) Admin deletes -> 200"
curl -s -X DELETE $URL/employees/1 -H "Authorization: Bearer $ADMIN"
echo
