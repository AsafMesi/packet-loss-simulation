# Comparing TCP and UDP with a Simple Example

This guide will walk you through the process of creating client-server scripts for both TCP and UDP protocols to demonstrate the differences in data transmission reliability. We will also cover how to simulate network issues using `netem` and create a Bash script to automate the process.

## Part 1: Python Client and Server Scripts

### TCP Scripts
#### Server (tcp_server.py)
```python
import socket
import sys

N = 10000  # Adjustable range of numbers
HOST = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("[TCP Server] Waiting for a connection...")

conn, addr = server_socket.accept()
print(f"[TCP Server] Connected by {addr}")

try:
    for i in range(1, N + 1):
        conn.sendall(f"{i}\n".encode())
finally:
    conn.close()
    server_socket.close()
    print("[TCP Server] Connection closed.")
```

#### Client (tcp_client.py)
```python
import socket

N = 10000  # Adjustable range of numbers
HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

received_data = []

try:
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        received_data.extend(map(int, data.splitlines()))
finally:
    client_socket.close()

expected_data = [i for i in range(1, N + 1)]

for i, (received, expected) in enumerate(zip(received_data, expected_data)):
    if received != expected:
        print(f"Mismatch at index {i}: received {received}, expected {expected}")

print("[TCP Client] Finished checking data.")
```

### UDP Scripts
#### Server (udp_server.py)
```python
import socket

N = 10000  # Adjustable range of numbers
HOST = '127.0.0.1'
PORT = 12346

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print("[UDP Server] Ready to send data...")

while True:
    data, addr = server_socket.recvfrom(1024)
    if data.decode().strip() == "GET DATA":
        for i in range(1, N + 1):
            server_socket.sendto(f"{i}\n".encode(), addr)
```

#### Client (udp_client.py)
```python
import socket

N = 10000  # Adjustable range of numbers
HOST = '127.0.0.1'
PORT = 12346

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto(b"GET DATA", (HOST, PORT))

received_data = []

try:
    while True:
        data, _ = client_socket.recvfrom(1024)
        if not data:
            break
        received_data.extend(map(int, data.decode().splitlines()))
except socket.timeout:
    print("[UDP Client] Timeout reached.")

client_socket.close()

expected_data = [i for i in range(1, N + 1)]

for i, (received, expected) in enumerate(zip(received_data, expected_data)):
    if received != expected:
        print(f"Mismatch at index {i}: received {received}, expected {expected}")

print("[UDP Client] Finished checking data.")
```

## Part 2: Simulating Network Issues with `netem`

`netem` is a Linux utility that allows you to introduce artificial delays, packet losses, duplication, and reordering to your network traffic.

### Install `netem`
Most Linux distributions already include `netem` as part of the `tc` (traffic control) package. You can install it using:
```bash
sudo apt-get install iproute2
```

### Apply Packet Loss
To simulate packet loss of 10% on `lo` (loopback interface), run:
```bash
sudo tc qdisc add dev lo root netem loss 10%
```

### Remove Packet Loss
To reset the network interface to normal:
```bash
sudo tc qdisc del dev lo root netem
```

## Part 3: Automating with a Bash Script
Create a Bash script to automate the entire process.

#### Script (run_test.sh)
```bash
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

### Usage
1. Make the script executable:
   ```bash
   chmod +x run_test.sh
   ```
2. Run the script:
   ```bash
   ./run_test.sh tcp
   ```

You can replace `tcp` with `udp` to test UDP.

## Explanation of Results
- **TCP:** You should see no mismatches because TCP ensures reliable delivery of data.
- **UDP:** You may observe mismatches or missing data due to the lack of reliability in UDP.

By following this guide, you can easily observe the practical differences between TCP and UDP and how network conditions affect data transmission.

