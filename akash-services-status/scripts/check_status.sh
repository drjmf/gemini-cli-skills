#!/bin/bash
echo "Checking Akash services status..."
echo "================================="

for service in /mnt/data/system/services/*/manager-*.sh /mnt/data/system/applications/*/manager-*.sh; do
    if [ -f "$service" ]; then
        echo "--- $(basename $(dirname $service)) ---"
        $service status
        echo ""
    fi
done

echo "Checking for zombie processes..."
echo "================================"
zombies=$(ps auxf | grep '[d]efunct' | wc -l)
echo "Found $zombies zombie processes."
if [ "$zombies" -gt 0 ]; then
  echo "The Reaper service is responsible for handling zombie processes."
fi