import socket

N = 10000  # Adjustable range of numbers
HOST = '127.0.0.1'
PORT = 12346

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5)
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