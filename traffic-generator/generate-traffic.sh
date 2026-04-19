#!/bin/sh
# generate-traffic.sh — hits pay-api continuously so we have interesting metrics.

echo "Waiting 10s for pay-api to be ready..."
sleep 10

echo "Starting traffic generation..."
while true; do
  curl -s -o /dev/null http://pay-api:5000/
  curl -s -o /dev/null http://pay-api:5000/payment
  curl -s -o /dev/null http://pay-api:5000/payment
  curl -s -o /dev/null http://pay-api:5000/payment
  curl -s -o /dev/null http://pay-api:5000/health
  sleep 1
done

