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