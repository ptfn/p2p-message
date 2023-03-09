from colorama import Fore, init, Back
from datetime import datetime
from threading import Thread
from random import choice
import argparse
import socket
import time


class P2P():
    def __init__(self,
                 _name: str,
                 _port: int,
                 _first: bool,
                 _max_clients: int,
                 _port_peer: int):
        self.name = _name
        self.port = _port
        self.first = _first
        self.num_client = 0
        self.max_clients = _max_clients
        self.clients_colors = []
        self.clients_ip = [() for i in range(self.max_clients)]  # Set?
        self.servers_ip = [() for i in range(self.max_clients)]  # Set?
        self.address_server = ('192.168.0.160', _port_peer)
        self.clients_sock = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(self.max_clients)]
        self.colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN,
                       Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX,
                       Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
                       Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX,
                       Fore.LIGHTYELLOW_EX, Fore.MAGENTA,
                       Fore.RED, Fore.YELLOW]

    def run(self):
        thread_client = Thread(target=self.client)
        thread_server = Thread(target=self.server)
        thread_server.start()
        if not(self.first):
            thread_client.start()
        self.send_to_client()

    def client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect(self.address_server)
        client_sock.sendto(f"G {self.port}".encode(), self.address_server)

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

        status = '│Host: {} Port: {}│'.format(socket.gethostname(), self.port)
        print(f"┌{'─' * (len(status)-20)}{' Start Server '}{'─' * (len(status)-20)}┐")
        print(status)
        print(f"└{'─' * (len(status)-2)}┘", sep='')

        while True:
            data, address = self.server_sock.recvfrom(1024)
            string = data.decode().split(' ')
            port = int(string[1])

            if (address[0], port) not in self.servers_ip:
                if string[0] == "G":
                    self.server_sock.sendto((f"{(self.address_server[0], self.port)}").encode(), address)
                    if self.num_client > 0:
                        for server in self.servers_ip:
                            if server != ():
                                self.server_sock.sendto((f"{server}").encode(),
                                                        address)
                    self.server_sock.sendto(b'Not address', address)
                else:
                    if self.num_client <= self.max_clients-1:
                        self.clients_ip[self.num_client] = address
                        self.servers_ip[self.num_client] = address[0], port
                        self.connect_client(self.clients_sock[self.num_client],
                                            int(port),
                                            address[0])
                        self.num_client += 1
                        # Problem with number clients
                        # Number client not here.
                        # He must be in func connect_client
                        print('\r[*] Added {} {}'.format(address[0], port))

    def connect_client(self, sock, port, address):
        try:
            server = address, port
            sock.connect(server)
            sock.sendto(f"C {self.port}".encode(), server)

            color = choice(self.colors)
            self.clients_colors.append(color)

            thread = Thread(target=self.listen, args=[sock])
            thread.start()
        except Exception:
            print('[*] Connect To {} Failed!'.format(server))

    def listen(self, sock):
        # Her failed connect and close sock
        while True:
            data = sock.recv(1024)
            if not data:
                break
            print('\r{}\n[{}]: '.format(data.decode(), self.name), end='')

    def send_to_client(self):
        time.sleep(2)
        while True:
            try:
                message = input('[{}]: '.format(self.name))
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                for i in range(len(self.clients_ip)):
                    if self.clients_ip[i] != ():
                        to_send = f"{self.clients_colors[i]}[{date_now}] {self.name}: {Fore.RESET}{message}"
                        self.server_sock.sendto(to_send.encode(),
                                                self.clients_ip[i])
            except Exception as e:
                print(e)
                # Her exit program
                # Close socket
                # print('Exit')
                # exit(0)


def main():
    parser = argparse.ArgumentParser(description="p2p chat")
    parser.add_argument("-p", "--port",
                        type=int,
                        dest="port",
                        default=55555,
                        help="port for you server")
    parser.add_argument("-n", "--name",
                        type=str,
                        dest="name",
                        default="user",
                        help="the name to display in chat")
    parser.add_argument("-pp", "--port-peer",
                        type=int,
                        dest="peer",
                        default=11111,
                        help="port to connect to the peer")
    parser.add_argument("-f", "--first",
                        default=False,
                        action="store_true",
                        dest="first",
                        help="fisrt peer")
    parser.add_argument("-m", "--max",
                        type=int,
                        default=10,
                        dest="max",
                        help="max client")

    args = parser.parse_args()

    p2p = P2P(_name=args.name,
              _port=args.port,
              _port_peer=args.peer,
              _first=args.first,
              _max_clients=args.max)
    p2p.run()


if __name__ == "__main__":
    main()
