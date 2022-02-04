import socket
import sys
import threading
import datetime
import random

def main():
    # ----SERVER----
    class Server():
        def __init__(self):
            self.running = True
            self.thread = None
            self.host = None
            self.port = None
            self.conn = None
            self.addr = None
            self.name = None
            self.color = random.randint(30, 37)

        def read_conn(self):
            while self.running == True:
                msg = (self.conn.recv(1024)).decode()
                if not msg: break
                print(msg)

        def kill(self):
            self.running = False

        def now(self):
            dt = datetime.datetime.now()
            return dt.strftime("%H:%M:%S")

        def run(self):
            self.host = "0.0.0.0"
            self.port = int(sys.argv[1])
            self.name = input("Name:")
            print("--------------------")

            # CONNECT
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, self.port))
            sock.listen(1)
            self.conn, self.addr = sock.accept()
            self.conn.send(("! Connected to {}\n".format(self.name)).encode())

            self.thread = threading.Thread(target=self.read_conn, args=())
            self.thread.start()
            
            # MESSAGES
            while True:
                try:
                    msg = input("")
                    self.conn.send(("{} <\033[{}m{}\033[0m> : ".format(self.now(),self.color, self.name) + msg).encode())
                except KeyboardInterrupt:
                    print("\n--------------------")
                    self.conn.send(("\n! {} left".format(self.name)).encode())
                    self.kill()
                    sock.close()
                    break



    # ----CLIENT----
    class Client():
        def __init__(self):
            self.running = True
            self.thread = None
            self.host = None
            self.port = None
            self.sock = None
            self.name = None
            self.color = random.randint(30, 37)

        def read_sock(self):
            while self.running == True:
                msg = (self.sock.recv(1024)).decode()
                if not msg: break
                print(msg)

        def kill(self):
            self.running = False

        def now(self):
            dt = datetime.datetime.now()
            return dt.strftime("%H:%M:%S")

        def run(self):
            self.host = input("Host:")
            self.port = int(sys.argv[1])
            self.name = input("Name:")
            print("--------------------")

            # CONNECT
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.send(("! Connected to {}\n".format(self.name)).encode())

            self.thread = threading.Thread(target=self.read_sock, args=())
            self.thread.start()
            
            # MESSAGES
            while True:
                try:
                    msg = input("")
                    self.sock.send(("{} <\033[{}m{}\033[0m> : ".format(self.now(),self.color, self.name) + msg).encode())
                except KeyboardInterrupt:
                    print("\n--------------------")
                    self.kill()
                    self.sock.send(("\n! {} left".format(self.name)).encode())
                    self.sock.close()
                    break


    choice = input("Server/Connect:")

    if choice == "server" or choice == "Server" or choice == "s":
        server = Server()
        server.run()
    elif choice == "connect" or choice == "Connect" or choice == "c":
        client = Client()
        client.run()
    else:
        print("Error!")

if __name__ == '__main__':
    main()

class P2P:
    def __init__(self, port, max_client=1):
        pass
