from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import socket

HOST = '127.0.0.1'
PORT = 1337

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class WorkerReceiver(QtCore.QObject):
    progress = QtCore.pyqtSignal(str)

    def run(self):
        while True:
            try:
                response = client.recv(1024)
                response = response.decode()
                self.progress.emit(response)
            except:
                client.close()
                break


class Ui_Dialog(QtWidgets.QWidget):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(464, 498)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.sendButton = QtWidgets.QPushButton(Dialog)
        self.sendButton.setGeometry(QtCore.QRect(370, 420, 89, 31))
        self.sendButton.setObjectName("sendButton")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(-10, 380, 481, 20))
        self.line.setLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.chatWindow = QtWidgets.QTextEdit(Dialog)
        self.chatWindow.setGeometry(QtCore.QRect(10, 10, 441, 371))
        self.chatWindow.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0.0284091, x2:1, y2:1, stop:0 rgba(136, 0, 255, 255), stop:1 rgba(188, 0, 255, 255));\n"
            "color: rgb(238, 238, 236);")
        self.chatWindow.setOverwriteMode(False)
        self.chatWindow.setObjectName("chatWindow")
        self.sendMessage = QtWidgets.QTextEdit(Dialog)
        self.sendMessage.setGeometry(QtCore.QRect(10, 410, 351, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sendMessage.sizePolicy().hasHeightForWidth())
        self.sendMessage.setSizePolicy(sizePolicy)
        self.sendMessage.setSizeIncrement(QtCore.QSize(0, 0))
        self.sendMessage.setBaseSize(QtCore.QSize(0, 0))
        self.sendMessage.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sendMessage.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sendMessage.setLineWidth(1)
        self.sendMessage.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.sendMessage.setObjectName("sendMessage")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.username = ""

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Chat Room"))
        self.sendButton.setText(_translate("Dialog", "Send"))
        self.chatWindow.setHtml(_translate("Dialog",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Send anytime &quot;q&quot; to leave</p>\n"
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To send private message, type: &quot;/private to [username] [message]&quot;</p>\n"
                                           "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.sendMessage.setHtml(_translate("Dialog",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.sendMessage.setPlaceholderText(_translate("Dialog", "Write username here..."))

        self.sendButton.clicked.connect(self.change_placeholder)
        self.sendButton.clicked.connect(self.receive_task)

    def change_placeholder(self):
        _translate = QtCore.QCoreApplication.translate
        self.sendMessage.setPlaceholderText(_translate("Dialog", "Write message here..."))
        print("[change_placeholder] called")
        if self.username == "":
            self.username = self.sendMessage.toPlainText()
            self.sendMessage.clear()
        if self.username == "q":
            client.close()
            self.chatWindow.append('\n' + "Goodbye!")
        client.connect((HOST, PORT))
        client.send(bytearray(self.username, encoding='utf-8'))
        status = client.recv(1024)
        status = status.decode()
        self.chatWindow.append(status)
        self.sendButton.clicked.connect(self.client_send)
        self.sendButton.clicked.disconnect(self.change_placeholder)

    def receive_task(self):
        self.work = WorkerReceiver()
        self.thread = QtCore.QThread(parent=self)
        self.work.progress.connect(self.append_message)
        self.work.moveToThread(self.thread)
        self.thread.started.connect(self.work.run)
        self.thread.start()

    def append_message(self, msg):
        self.chatWindow.append(f"{msg}")


    def client_send(self):
        self.message = self.sendMessage.toPlainText()
        self.sendMessage.clear()
        while True:
            if self.message == "q":
                client.send(bytearray(self.username + ": " + self.message, encoding='utf-8'))
                client.close()
                exit("Goodbye!")
                break
            client.send(bytearray(self.username + ": " + self.message, encoding='utf-8'))
            self.chatWindow.append(f"You: {self.message}")
            break


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    ui = Ui_Dialog()
    ui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())
    client.close()
