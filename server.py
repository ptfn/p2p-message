import socket

clients = []
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('192.168.0.160', 55555))
print('--- Start Server ---')

while True:
    data, address = sock.recvfrom(1024)
    port = int(data.decode())
    print('* Connect to server', address, port)

    if (address[0], port) not in clients:
        if clients:
            for client in clients:
                sock.sendto(('{}'.format(client)).encode(), address)
        sock.sendto(b'Not address', address)
        clients.append((address[0], port))
