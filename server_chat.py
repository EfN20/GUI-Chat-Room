import socket
from _thread import *
import psycopg2

conn = psycopg2.connect(host='localhost', database='python-lab7', port=5432, user='postgres', password='159753')
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS message_logs(\
               id serial primary key,\
               username varchar(255),\
               message varchar(255)\
               );")
conn.commit()

HOST = '127.0.0.1'
PORT = 1337
clients = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(10)
print(f"[ SERVER ] Listening for connection: [ PORT ]: {PORT}, [ HOST ]: {HOST}")


def client_thread(client, address):
    client.send(bytearray("You are connected", encoding='utf-8'))
    while True:
        try:
            message = client.recv(1024)
            if message:
                message = message.decode()
                print(message)
                sender = message.split(": ", 1)[0]
                text = message.split(": ", 1)[1]
                print("[TEST CURSOR]")
                print(f"[SENDER] {sender}")
                print(f"[TEXT] {text}")
                cursor.execute("INSERT INTO message_logs(username, message) VALUES (%s, %s)", (sender, text))

                if text.startswith("/private to"):
                    private_message = text[12:]
                    # print(f"[PRIVATE MESSAGE] {private_message}")
                    private_receiver = private_message.split(" ", 1)[0]
                    private_text = private_message.split(" ", 1)[1]
                    # print(f"[PRIVATE RECEIVER] {private_receiver}")
                    # print(f"[PRIVATE TEXT] {private_text}")
                    for receiver in clients.keys():
                        if clients.get(receiver) == private_receiver and receiver != client:
                            try:
                                receiver.send(bytearray(sender + " [PRIVATE]: " + private_text, encoding='utf-8'))
                                conn.commit()
                            except:
                                receiver.close()
                                clients.pop(receiver)
                elif text == "q":
                    for receiver in clients.keys():
                        if receiver == client:
                            # print("[Quit] is working")
                            receiver.close()
                            clients.pop(receiver)
                        if receiver != client:
                            try:
                                receiver.send(bytearray(sender + " is leaving the chat", encoding='utf-8'))
                            except:
                                receiver.close()
                                clients.pop(receiver)
                else:
                    for receiver in clients.keys():
                        if receiver != client:
                            try:
                                receiver.send(bytearray(message, encoding='utf-8'))
                                conn.commit()
                            except:
                                receiver.close()
                                clients.pop(receiver)
        except:
            continue


while True:
    client, address = server.accept()
    if client not in clients:
        username = client.recv(1024)
        clients[client] = username.decode()
        print(f"[ SERVER ] {username.decode()} has connected")
        print(clients)

    start_new_thread(client_thread, (client, address))
# conn.close()
# server.close()
