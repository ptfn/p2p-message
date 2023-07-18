from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
from network import P2P
import argparse
import sys


class Window(object):
    def __init__(self, name, port, peer,
                 first, maxi, length_rsa, length_aes):
        self.p2p_args = [name, port, peer, first,
                         maxi, length_rsa, length_aes]

    def setupUi(self, MainWindow):
        # Window title and size
        MainWindow.setObjectName("p2pChat")
        MainWindow.resize(640, 480)

        # Central, i dont no
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # TextBrowser
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 30, 480, 410))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textBrowser.setFont(font)
        self.textBrowser.setObjectName("textBrowser")

        # List
        self.List = QtWidgets.QListWidget(self.centralwidget)
        self.List.setGeometry(QtCore.QRect(500, 30, 130, 410))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.List.setFont(font)
        self.List.setObjectName('List')

        # LineEdit
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 450, 480, 20))
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")

        # Button1
        self.Button1 = QtWidgets.QPushButton(self.centralwidget)
        self.Button1.setGeometry(QtCore.QRect(500, 450, 60, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Button1.setFont(font)
        self.Button1.setObjectName("Button1")

        # Button2
        self.Button2 = QtWidgets.QPushButton(self.centralwidget)
        self.Button2.setGeometry(QtCore.QRect(570, 450, 60, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Button2.setFont(font)
        self.Button2.setObjectName("Button2")

        # Menu
        self.menu_bar = QtWidgets.QMenuBar(self.centralwidget)

        self.chat_menu = self.menu_bar.addMenu("&Chat")
        self.help_menu = self.menu_bar.addMenu("&Help")

        # Export Chat
        export_action = QtWidgets.QAction(text="&Export",
                                          parent=self.centralwidget)
        export_action.setStatusTip("Export text chat in file")
        export_action.setShortcut("Ctrl+R")
        export_action.triggered.connect(self.export_text)
        self.chat_menu.addAction(export_action)

        self.chat_menu.addSeparator()

        # Exit
        exit_action = QtWidgets.QAction(text="&Exit",
                                        parent=self.centralwidget)
        exit_action.setStatusTip("Exit program")
        exit_action.setShortcut("Ctrl+E")
        exit_action.triggered.connect(self.quit)
        self.chat_menu.addAction(exit_action)

        # About
        about_action = QtWidgets.QAction(text='&About',
                                         parent=self.centralwidget)
        self.help_menu.addAction(about_action)
        about_action.setStatusTip('About')
        about_action.setShortcut('F1')

        # Main
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Init P2P
        self.p2p = P2P(_name=self.p2p_args[0],
                       _port=self.p2p_args[1],
                       _port_peer=self.p2p_args[2],
                       _first=self.p2p_args[3],
                       _max_clients=self.p2p_args[4],
                       _length_rsa=self.p2p_args[5],
                       _length_aes=self.p2p_args[6],
                       _textBrowser=self.textBrowser,
                       _list=self.List)

        # Create and Start Thread
        thread = Thread(target=self.p2p.run)
        thread.daemon = True
        thread.start()

        # Connect Buttons
        self.Button1.clicked.connect(lambda: self.input_text())
        self.Button1.setShortcut("Ctrl+S")
        self.Button2.clicked.connect(lambda: self.clear_text())
        self.Button2.setShortcut("Ctrl+C")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("p2pChat", "p2pChat"))
        self.Button1.setText(_translate("p2pChat", "Send"))
        self.Button2.setText(_translate("p2pChat", "Clear"))

    def input_text(self):
        text = self.lineEdit.text()
        self.lineEdit.clear()
        self.p2p.send_to_client(text)

    def clear_text(self):
        self.textBrowser.clear()

    def export_text(self):
        text = self.textBrowser.toPlainText()
        with open("chat.txt", "+a") as f:
            f.write(f"{text}\n")
        self.textBrowser.clear()

    def quit(self):
        self.p2p.send_to_client("/exit")
        sys.exit()


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

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = Window(name=args.name,
                port=args.port,
                peer=args.peer,
                first=args.first,
                maxi=args.max,
                length_rsa=args.length_rsa,
                length_aes=args.length_aes)

    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
