#!/bin/bash
payload=$(cat ${1:-payload.json})

SECRET_KEY=my_secret_key
signature=$(echo -n "$payload" | openssl sha1 -hmac "$SECRET_KEY" | awk '{print "sha1="$1}')
signature=$(echo -n "$payload" | openssl sha256 -hmac "$SECRET_KEY" | awk '{print "sha256="$1}')

echo ${signature}
curl -X POST \
  http://127.0.0.1:8080/jenkins-webhook?dryrun=true \
  -H 'Content-Type: application/json' \
  -H 'X-Event-Key: repo:push' \
  -H "X-Hub-Signature: ${signature}" \
  -d "${payload}"
