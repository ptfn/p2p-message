from colorama import Fore, init, Back
from datetime import datetime
from threading import Thread
from random import choice
import argparse
import socket
import time
import sys
import rsa


class P2P():
    def __init__(self, _name: str, _port: int, _first: bool,
                 _max_clients: int, _port_peer: int):
        # Initial data for server and client startup
        self.length_key = 2048  # It`s slow, but have high secure
        self.name = _name
        self.port = _port
        self.first = _first
        self.num_client = 0
        self.max_clients = _max_clients
        # Structures for storing clients and servers
        self.clients_colors = list()
        self.clients_ip = dict()
        self.servers_ip = set()
        self.address_server = ('192.168.0.160', _port_peer)
        self.clients_sock = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for i in range(self.max_clients)]
        self.colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN,
                       Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX,
                       Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
                       Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX,
                       Fore.LIGHTYELLOW_EX, Fore.MAGENTA,
                       Fore.RED, Fore.YELLOW]
        # RSA
        print("[*] Generate RSA keys...")
        self.generate_keys()
        print("[*] Generated completed!")
        self.private_key, self.public_key = self.load_keys()

    # RSA - we need a separate class for this!!!
    # Generate keys RSA
    def generate_keys(self):
        (public_key, private_key) = rsa.newkeys(self.length_key)
        with open('pub.pem', 'wb') as p:
            p.write(public_key.save_pkcs1('PEM'))
        with open('sec.pem', 'wb') as p:
            p.write(private_key.save_pkcs1('PEM'))

    # Load keys RSA
    def load_keys(self):
        with open('pub.pem', 'rb') as p:
            public_key = rsa.PublicKey.load_pkcs1(p.read())
        with open('sec.pem', 'rb') as p:
            private_key = rsa.PrivateKey.load_pkcs1(p.read())
        return private_key, public_key

    # NETWORK
    # Function to start in the server and client threads
    # and switch to data transfer
    def run(self):
        self.thread_server = Thread(target=self.server)
        self.thread_server.daemon = True
        self.thread_server.start()

        if not(self.first):
            self.thread_client = Thread(target=self.client)
            self.thread_client.start()

        self.send_to_client()

    # Function for getting primary addresses from first peer
    def client(self):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.connect(self.address_server)
        client_sock.sendto(f"G {self.port}".encode(), self.address_server)

        while True:
            data = client_sock.recv(4084).decode()

            if data.strip() == 'Not address':
                break

            else:
                address = data.split(',')[0][2:]
                port = data.split(',')[1]
                # Need add client?
                self.connect_client(self.clients_sock[self.num_client],
                                    int(port[:len(port)-1]),
                                    address[:len(address)-1])
                self.num_client += 1

        client_sock.close()

    # Primary server for receiving, connecting and transferring new clients
    def server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind(('', self.port))

        status = f"│Host: {socket.gethostname()} Port: {self.port}│"
        len_line = round((len(status)-16)/2)
        the_end = len_line if len(status) % 2 == 0 else len_line-1

        print(f"┌{'─' * (len_line)} Start Server {'─' * (the_end)}┐")
        print(status)
        print(f"└{'─' * (len(status)-2)}┘", sep='')

        while True:
            data, address = self.server_sock.recvfrom(4084)
            print(data)

            if not data:
                break

            string = data.decode().split(' ')
            port = int(string[1])

            if (address[0], port) not in self.servers_ip:
                # Transferring peers to the client
                if string[0] == "G":
                    self.server_sock.sendto((f"{(self.address_server[0], self.port)}").encode(), address)

                    if self.num_client > 0:
                        for server in self.servers_ip:
                            self.server_sock.sendto((f"{server}").encode(),
                                                    address)
                    self.server_sock.sendto(b'Not address', address)
                # Connecting server
                else:
                    if self.num_client <= self.max_clients-1:
                        # Convert string to public_key
                        str_pub_key = ' '.join(string[2:]).encode()
                        public_key = rsa.PublicKey.load_pkcs1(str_pub_key)

                        self.clients_ip[address] = public_key
                        self.servers_ip.add((address[0], port))
                        self.connect_client(self.clients_sock[self.num_client],
                                            int(port),
                                            address[0])
                        self.num_client += 1
                        print('\r[*] Added {} {}'.format(address[0], port))

    # Client connections to the server
    def connect_client(self, sock, port, address):
        try:
            server = address, port
            string_public_key = self.public_key.save_pkcs1('PEM').decode()
            sock.connect(server)
            sock.sendto(f"C {self.port} {string_public_key}".encode(), server)

            color = choice(self.colors)
            self.clients_colors.append(color)

            # Sending a listening function to the stream
            thread = Thread(target=self.listen, args=[sock])
            thread.daemon = True
            thread.start()

        except Exception:
            print('\r[*] Connect To {} Failed!'.format(server))

    # Listening function, receives data and displays
    def listen(self, sock):
        while True:
            try:
                crypto, address = sock.recvfrom(4084)
                decrypt = rsa.decrypt(crypto, self.private_key)
                data = decrypt.decode()

                if not data:
                    break

                print('\r{}\n[{}]: '.format(data, self.name), end='')

                # Problem
                if data.split(' ')[2] == 'came':
                    self.servers_ip.discard(address)
                    break

            except Exception as e:
                print("Error in the listening segment!", e)

        sock.close()

    # Function for sending messages to all connected clients
    def send_to_client(self):
        time.sleep(1)

        while True:
            try:
                message = input('[{}]: '.format(self.name))
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if message != '/exit':
                    for i, (address, pub_key) in enumerate(self.clients_ip.items()):
                        to_send = f"{self.clients_colors[i]}[{date_now}] {self.name}: {Fore.RESET}{message}"
                        crypto = rsa.encrypt(to_send.encode(), pub_key)
                        self.server_sock.sendto(crypto, address)

                else:
                    # Need RSA
                    for i, (address, pub_key) in enumerate(self.clients_ip.items()):
                        to_send = f"[*] {self.name} came out!"
                        crypto = rsa.encrypt(to_send.encode(), pub_key)
                        self.server_sock.sendto(crypto, address)
                    # It work. Wow!
                    sys.exit()
            except Exception as e:
                print("Error in the sending segment!", e)


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
