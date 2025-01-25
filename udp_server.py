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