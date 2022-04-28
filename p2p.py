from threading import Thread
import datetime
import random
import socket
import time
import sys


def main():
    class Server(Thread):
        def __init__(self, port):
            Thread.__init__(self)
            self.port = port
            self.host = ""
            
            self.sock = None
            self.conn = None
            self.addr = None

        def run(self):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.conn, self.addr = self.sock.accept()
            
            while True:
                msg = (self.conn.recv(1024)).decode()
                if not msg: 
                    self.sock.close()
                    break
                print(msg)



    class Client(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.host = None
            self.port = None

            self.sock = None
            self.name = sys.argv[1]
            self.color = random.randint(30, 37)

        def now(self):
            dt = datetime.datetime.now()
            return dt.strftime("%H:%M:%S")

        def run(self):
            self.host = input("Host:")
            self.port = int(input("Port:"))
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))


            while True:
                try:
                    msg = input("")
                    self.sock.send(("{} <\033[{}m{}\033[0m> : ".format(self.now(),self.color, self.name) + msg).encode())
                except KeyboardInterrupt:
                    self.sock.send(("\n! {} left".format(self.name)).encode())
                    self.sock.close()
                    break


    port = int(sys.argv[2])

    server = Server(port)
    server.start()
    print("--- Starting Server ---")

    client = Client()
    print("--- Starting Client ---")
    client.start()

if __name__ == '__main__':
    main()
