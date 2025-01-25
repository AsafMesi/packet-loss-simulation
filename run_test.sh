#!/bin/bash

TYPE=$1

SERVER_SCRIPT="${TYPE}_server.py"
CLIENT_SCRIPT="${TYPE}_client.py"
PACKET_LOSS=10

if [ -z "$TYPE" ] || [ ! -f "$SERVER_SCRIPT" ] || [ ! -f "$CLIENT_SCRIPT" ]; then
  echo "Usage: $0 <type> (tcp / udp / kcp)"
  echo "Make sure you have the files <type>_server.py and <type>_client.py in the same directory"
  exit 1
fi

if [[ $(uname) != "Linux" ]]; then
  echo "[Error] This script is only supported on Linux."
  exit 1
fi

echo "[Bash Script] Detected Linux environment."

# Apply packet loss
if ! sudo tc qdisc add dev lo root handle 1: netem loss ${PACKET_LOSS}% 2>/dev/null; then
  echo "[Error] Failed to add netem qdisc. Ensure 'tc' is installed and supported on your system."
  exit 1
fi

echo "[Bash Script] Starting server..."
python3 $SERVER_SCRIPT &
SERVER_PID=$!

# Wait for server to initialize
sleep 1

echo "[Bash Script] Starting client..."
python3 $CLIENT_SCRIPT

# Shut down server
echo "[Bash Script] Shutting down server..."
kill $SERVER_PID

# Remove packet loss
sudo tc qdisc del dev lo root handle 1: 2>/dev/null || echo "[Warning] Failed to remove netem qdisc."

echo "[Bash Script] Test completed."
