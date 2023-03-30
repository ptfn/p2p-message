from crypto import Asymmetrical, Symmetrical
from colorama import Fore, init, Back
from datetime import datetime
from threading import Thread
from random import choice
import argparse
import socket
import time
import sys


class P2P():
    def __init__(self, _name: str, _port: int, _first: bool,
                 _max_clients: int, _port_peer: int,
                 _length_rsa: int, _length_aes: int):
        # Init library crypto for encrypt and decrypt message
        self.rsa = Asymmetrical()
        self.aes = Symmetrical()

        # Initial data for server and client startup
        self.name = _name
        self.port = _port
        self.first = _first
        self.num_client = 0
        self.length_rsa = _length_rsa  # It`s slow, but have high secure
        self.length_aes = _length_aes
        self.max_clients = _max_clients

        # Structures for storing clients and servers
        self.clients_colors = list()
        self.clients_name = list()
        self.clients_ip = dict()
        self.servers_ip = dict()
        self.address_server = ('localhost', _port_peer)
        self.clients_sock = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                             for i in range(self.max_clients)]
        self.colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN,
                       Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX,
                       Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
                       Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX,
                       Fore.LIGHTYELLOW_EX, Fore.MAGENTA,
                       Fore.RED, Fore.YELLOW]

        # CRYPTOGRAPHY
        # RSA
        print(f"[*] Generate RSA-{self.length_rsa} keys...")
        self.rsa.generate_keys(self.length_rsa)
        print("[*] Generated completed!")
        self.private_key, self.public_key = self.rsa.load_keys()

        # AES
        print(f"[*] Generate AES-{self.length_aes*8} key...")
        self.aes_key = self.aes.create_key(self.length_aes)
        print("[*] Generated completed!")

    # P2P NETWORK
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
        try:
            client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_sock.connect(self.address_server)
            client_sock.sendto(f"G {self.port}".encode(),
                               self.address_server)

            while True:
                data = client_sock.recv(1024).decode()

                if data.strip() == 'Not address':
                    break

                else:
                    string = data.split(' ')
                    ip = string[0]
                    port = int(string[1])
                    self.connect_client(self.clients_sock[self.num_client],
                                        port, ip)
                    self.num_client += 1

            client_sock.close()
        except ConnectionRefusedError:
            print("[!] Connect refused!")

    # Primary server for receiving, connecting and transferring new clients
    def server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_sock.bind(('', self.port))

        status = f"│Host: {socket.gethostname()} Port: {self.port}│"
        length = round((len(status)-16)/2)
        the_end = length if len(status) % 2 == 0 else length-1

        start = f"┌{'─' * (length)} Start Server {'─' * (the_end)}┐\n" \
                f"{status}\n" \
                f"└{'─' * (len(status)-2)}┘"

        print(start)

        while True:
            data, address = self.server_sock.recvfrom(1024)
            string = data.decode().split(' ')
            port = int(string[1])

            try:
                name = string[2]
                if name not in self.clients_name:
                    self.clients_name.append(name)
                    self.list.addItem(name)
            except Exception:
                pass

            if (address[0], port) not in self.servers_ip:
                # Transferring peers to the client
                if string[0] == "G":
                    to_send = f"{self.address_server[0]} {self.port}"
                    self.server_sock.sendto(to_send.encode(), address)

                    if self.num_client > 0:
                        for server in self.servers_ip:
                            to_send = f"{server[0]} {server[1]}".encode()
                            self.server_sock.sendto(to_send, address)
                    self.server_sock.sendto(b'Not address', address)

                # Connecting server
                else:
                    if self.num_client <= self.max_clients-1:
                        # Key exchange
                        server_key = self.public_key.save_pkcs1('PEM').decode()
                        self.server_sock.sendto((f"{server_key}").encode(),
                                                address)
                        data = self.server_sock.recv(1024)
                        key = self.rsa.decrypt(data, self.private_key)

                        # Added client
                        self.clients_ip[address] = key
                        self.servers_ip[(address[0], port)] = key
                        sock = self.clients_sock[self.num_client]

                        thread = Thread(target=self.connect_client,
                                        args=[sock, int(port), address[0]])
                        thread.daemon = True
                        thread.start()

                        self.num_client += 1
                        print('\r[*] Added {} {}'.format(address[0], port))

    # Client connections to the server
    def connect_client(self, sock, port, address):
        try:
            server = address, port
            sock.connect(server)
            print(f"\r[*] Connections to {server[0]} {server[1]}")
            sock.sendto((f"C {self.port} {self.name}").encode(), server)

            # Key exchange
            data = sock.recv(1024).decode()
            public_key = self.rsa.convert(data, '')
            crypto = self.rsa.encrypt(self.aes_key, public_key)
            sock.sendto(crypto, server)

            color = choice(self.colors)
            self.clients_colors.append(color)

            # Sending a listening function to the stream
            thread = Thread(target=self.listen, args=[sock])
            thread.daemon = True
            thread.start()

        except Exception as e:
            print('\r[!] Connect To {} Failed!'.format(server), e)

    # Listening function, receives data and displays
    def listen(self, sock):
        while True:
            try:
                cipher, address = sock.recvfrom(1024)
                tag, address = sock.recvfrom(1024)
                nonce, address = sock.recvfrom(1024)

                text = self.aes.decrypt(self.aes_key, cipher, tag, nonce)
                text = text.decode()

                if not cipher and not nonce:
                    break

                print('\r{}\n[{}]: '.format(text, self.name), end='')

                if text.split(' ')[2] == 'came':
                    del self.servers_ip[address]
                    break

            except Exception as e:
                print("[!] Error in the listening segment!", e)

        sock.close()

    # Function for sending messages to all connected clients
    def send_to_client(self):
        time.sleep(1)

        while True:
            try:
                message = input('[{}]: '.format(self.name))
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if message != '/exit':
                    for i, (addr, key) in enumerate(self.clients_ip.items()):
                        to_send = f"{self.clients_colors[i]}[{date_now}] " \
                                f"{self.name}: {Fore.RESET}{message}"
                        cipher, tag, nonce = self.aes.encrypt(key,
                                                            to_send.encode())

                        self.server_sock.sendto(cipher, addr)
                        self.server_sock.sendto(tag, addr)
                        self.server_sock.sendto(nonce, addr)

                else:
                    for i, (addr, key) in enumerate(self.clients_ip.items()):
                        to_send = f"[*] {self.name} came out!"
                        cipher, tag, nonce = self.aes.encrypt(key,
                                                            to_send.encode())

                        self.server_sock.sendto(cipher, addr)
                        self.server_sock.sendto(tag, addr)
                        self.server_sock.sendto(nonce, addr)
                    # It work. Wow!
                    sys.exit()
            except Exception as e:
                print("[!] Error in the sending segment!", e)


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

    parser.add_argument("-lr", "--length_rsa",
                        type=int,
                        default=1024,
                        dest="length_rsa",
                        help="length RSA keys")

    parser.add_argument("-la", "--length_aes",
                        type=int,
                        default=16,
                        dest="length_aes",
                        help="length AES key")

    args = parser.parse_args()

    p2p = P2P(_name=args.name,
              _port=args.port,
              _port_peer=args.peer,
              _first=args.first,
              _max_clients=args.max,
              _length_rsa=args.length_rsa,
              _length_aes=args.length_aes)

    p2p.run()


if __name__ == "__main__":
    main()
