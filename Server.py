from queue import Queue
from socket import *
from time import ctime
import os
import time
import _thread
import Files

BUFSIZE = 1024
CONFIRM = False
HOST = '127.0.0.1'
PORT = 12000
ADDR = (HOST, PORT)
tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.bind(ADDR)
tcp_socket.listen(100)

user_list = []
user_queue = {}
active_user = []
active_user_list = []


def recv(this_tcp_socket):
    while True:
        try:
            print(this_tcp_socket)
            uid = this_tcp_socket.recv(BUFSIZE).decode('utf-8')
        except:
            print('Disconnected')
            return None
        if uid not in user_list:
            user_list.append(uid)
            active_user_list.append(uid)
            user_queue[uid] = Queue()
            print(uid + ' signed up ' + ctime())
        else:
            if uid in active_user_list:
                server_message = 'FROM SERVER:' + uid + ' already logged in'
                this_tcp_socket.send(server_message.encode('utf-8'))
                return None
            else:
                active_user_list.append(uid)
                print(uid + ' logged in ' + ctime())
        user = User(this_tcp_socket, uid)
        active_user.append(user)
        user.recv()


def send():
    global CONFIRM
    while True:
        for eachUser in active_user:
            if eachUser.offline:
                active_user.remove(eachUser)
                # del eachUser
                continue
            while user_queue[eachUser.uid].qsize():
                message_to_send = user_queue[eachUser.uid].get()
                # print(message_to_send)
                eachUser.socket.send(message_to_send.encode('utf-8'))
                time.sleep(0.1)
                if message_to_send.startswith('FILE'):
                    file_header = message_to_send.split(',')
                    message_to_send = user_queue[eachUser.uid].get()
                    # print(message_to_send)
                    eachUser.socket.send(message_to_send.encode('utf-8'))
                    time.sleep(0.1)
                    while 1:
                        if CONFIRM:
                            CONFIRM = False
                            break
                    file_size = int(file_header[2])
                    # file_name = file_header[1]
                    recv_size = 0
                    while recv_size < file_size:
                        line = user_queue[eachUser.uid].get()
                        eachUser.socket.send(line)
                        recv_size += len(line)
                        # print(recv_size, '/', file_size)
                    time.sleep(0.1)
                    # return file_size, file_name
                else:
                    pass


class User(object):

    def __init__(self, user_socket, uid):
        self.socket = user_socket
        self.uid = uid
        self.offline = False
        self.disconnected = False
        self.contact = None

    def recv(self):
        global CONFIRM
        while True:
            try:
                message_received = self.socket.recv(BUFSIZE).decode('utf-8')
            except timeout:
                print(self.uid + ' disconnected')
                active_user_list.remove(self.uid)
                self.offline = True
                return None
            if message_received == 'CONFIRM':
                CONFIRM = 1
            elif message_received == 'LOG OUT':
                active_user_list.remove(self.uid)
                print(self.uid + ' logged out ' + ctime())
                self.offline = True
                return None
            elif message_received.startswith('FILE'):
                file_size, file_name = Files.server_recv(self.socket, message_received)
                if self.contact is not None:
                    user_queue[self.contact].put(message_received)
                    receive_message = '\n->' + 'Receive a file:\n\n' + file_name + '\n\n->from ' \
                                      + self.uid + ', send to ' + self.contact + ' at ' \
                                      + ctime() + '\n'
                    user_queue[self.contact].put(receive_message)
                    send_file_name = './' + file_name
                    if not os.path.isfile(send_file_name):
                        print('file:', send_file_name, ' is not exists')
                        return
                    else:
                        with open(send_file_name, 'rb') as f:
                            for line in f:
                                user_queue[self.contact].put(line)
                else:
                    server_message = '\nCONTACT NEED TO CHOOSE!\n'
                    self.socket.send(server_message.encode('utf-8'))
                # delete the file from path!!!
            elif message_received.isdigit():
                if message_received in user_list:
                    self.contact = message_received
                else:
                    self.socket.send('\nUID NOT FOUND!\n'.encode('utf-8'))
            else:
                if self.contact is not None:
                    message_received = '\n->' + 'Receive from ' + self.uid + ', send to '\
                          + self.contact + ' at ' + ctime() + '\n' + message_received[1:] + '\n'
                    user_queue[self.contact].put(message_received)
                else:
                    server_message = '\nCONTACT NEED TO CHOOSE!\n'
                    self.socket.send(server_message.encode('utf-8'))


def main():
    _thread.start_new_thread(send, ())
    while True:
        new_tcp_socket, new_addr = tcp_socket.accept()
        print('connected from ', new_addr, ctime())
        _thread.start_new_thread(recv, (new_tcp_socket, ))


if __name__ == '__main__':
    main()
