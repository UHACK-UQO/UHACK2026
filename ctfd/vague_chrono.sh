#!/bin/sh
sleep $1

echo $4 | jq -c ".[]" | while read id; do
    curl -sk -X PATCH "${2}/api/v1/challenges/${id}" \
        --json '{"state":"visible"}' \
        -H "Authorization: Token ${3}" &> /dev/null
done