import threading
import socket
import sys


class P2P():
    def __init__(self, _name: str, _port: int, _max_clients: int = 10):
        self.name = _name
        self.port = _port
        self.num_client = 0
        self.max_clients = _max_clients
        self.clients_ip = [() for i in range(self.max_clients)]  # Set?
        self.servers_ip = [() for i in range(self.max_clients)]  # Set?
        self.address_server = ('', 55555)
        self.clients_sock = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(self.max_clients)]

    def run(self):
        thread_client = threading.Thread(target=self.client)
        thread_server = threading.Thread(target=self.server)
        thread_server.start()
        thread_client.start()
        self.send_to_client()

    def client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect(self.address_server)
        client_sock.sendto(f"{self.port}".encode(), self.address_server)

        while True:
            data = client_sock.recv(1024).decode()
            if data.strip() == 'Not address':
                break
            else:
                address = data.split(',')[0][2:]
                port = data.split(',')[1]
                self.connect_client(self.clients_sock[self.num_client],
                                    int(port[:len(port)-1]),
                                    address[:len(address)-1])
                self.num_client += 1
        client_sock.close()

    def server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind(('', self.port))
        print('\r--- Start Server ---')
        print('\r({} / {})'.format(socket.gethostname(), self.port))

        while True:
            data, address = self.server_sock.recvfrom(1024)
            port = int(data.decode())

            if (address[0], port) not in self.servers_ip:
                if self.num_client <= self.max_clients-1:
                    self.clients_ip[self.num_client] = address
                    self.servers_ip[self.num_client] = address[0], port
                    self.connect_client(self.clients_sock[self.num_client],
                                        int(port),
                                        address[0])
                    self.num_client += 1
                    # Problem with number clients
                    print('\rAdded', address[0], port)

    def connect_client(self, sock, port, address):
        try:
            server = address, port
            sock.connect(server)
            sock.sendto(f"{self.port}".encode(), server)

            thread = threading.Thread(target=self.listen, args=[sock])
            thread.start()
        except Exception:
            print('Connect To {} Failed!'.format(server))

    def listen(self, sock):
        while True:
            data = sock.recv(1024)
            if not data:
                break
            print('\r{}'.format(data.decode()))

    def send_to_client(self):
        while True:
            try:
                message = input('> ')
                for i in range(len(self.clients_ip)):
                    if self.clients_ip[i] != ():
                        self.server_sock.sendto((f"[{self.name}]:{message}").encode(),
                                                self.clients_ip[i])
            except Exception as e:
                print(e)
                # print('Exit')
                # exit(0)


def main():
    p2p = P2P(str(sys.argv[2]), int(sys.argv[1]))
    p2p.run()


if __name__ == "__main__":
    main()
