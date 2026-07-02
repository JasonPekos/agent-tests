#!/bin/bash
# Verifier. Harbor copies tests/ into the container AFTER the agent finishes
# (so the agent can never read it) and runs this script. The whole contract:
# write a reward in [0, 1] to /logs/verifier/reward.txt.

expected="3"
actual="$(tr -d '[:space:]' < /app/answer.txt 2>/dev/null)"

if [ "$actual" = "$expected" ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo "expected '$expected', got '$actual'" >&2
  echo 0 > /logs/verifier/reward.txt
fi
