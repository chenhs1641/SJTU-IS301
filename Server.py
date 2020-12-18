import os
import threading
import time
from queue import Queue
from socket import *
from time import ctime

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
group_active_user_list = []
group_user_list = []


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
            if uid in active_user_list or uid in group_active_user_list:
                server_message = 'REPEAT LOGIN'
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
                if eachUser.uid in active_user_list:
                    active_user_list.remove(eachUser.uid)
                if eachUser.uid in group_active_user_list:
                    group_active_user_list.remove(eachUser.uid)
                print(eachUser.uid + ' is offline at ' + ctime())
                active_user.remove(eachUser)
                continue
            while user_queue[eachUser.uid].qsize():
                message_to_send = user_queue[eachUser.uid].get()
                eachUser.socket.send(message_to_send.encode('utf-8'))
                time.sleep(0.1)
                if message_to_send.startswith('FILE'):
                    file_header = message_to_send.split(',')
                    message_to_send = user_queue[eachUser.uid].get()
                    eachUser.socket.send(message_to_send.encode('utf-8'))
                    time.sleep(0.1)
                    while 1:
                        if CONFIRM:
                            CONFIRM = False
                            break
                    file_size = int(file_header[2])
                    recv_size = 0
                    while recv_size < file_size:
                        line = user_queue[eachUser.uid].get()
                        eachUser.socket.send(line)
                        recv_size += len(line)
                    time.sleep(0.1)
                else:
                    pass


class User(object):

    def __init__(self, user_socket, uid):
        self.socket = user_socket
        self.uid = uid
        self.offline = False
        self.contact = None

    def recv(self):
        global CONFIRM
        while True:
            try:
                message_received = self.socket.recv(BUFSIZE).decode('utf-8')
            except:
                self.offline = True
                return None
            if message_received.isdigit():
                if message_received in user_list:
                    self.contact = message_received
                else:
                    self.socket.send('\nUID NOT FOUND!\n'.encode('utf-8'))
            elif message_received == 'LOG OUT':
                self.offline = True
                return None
            elif message_received.startswith('FILE'):
                message_header = message_received.split(',')
                file_size = int(message_header[2])
                file_name = message_header[1]
                with open('./' + file_name, 'wb') as f:
                    recv_size = 0
                    while recv_size < file_size:
                        line = self.socket.recv(BUFSIZE)
                        f.write(line)
                        recv_size += len(line)
                if self.contact is not None:
                    user_queue[self.contact].put(message_received)
                    receive_message = '\n->' + 'Receive a file:\n\n' + file_name +\
                                      '\n\n->from ' + self.uid + ', send to ' +\
                                      self.contact + ' at ' + ctime() + '\n'
                    user_queue[self.contact].put(receive_message)
                    send_file_name = './' + file_name
                    if not os.path.isfile(send_file_name):
                        print('file:', send_file_name, ' is not exists')
                        return
                    else:
                        with open(send_file_name, 'rb') as f:
                            for line in f:
                                user_queue[self.contact].put(line)
                    os.remove(send_file_name)
                else:
                    server_message = '\nCONTACT NEED TO CHOOSE!\n'
                    self.socket.send(server_message.encode('utf-8'))
            elif message_received == 'CONFIRM':
                CONFIRM = 1
            elif message_received.startswith('JOIN'):
                group_header = message_received.split(',')
                uid_group = group_header[1]
                active_user_list.remove(uid_group)
                group_active_user_list.append(uid_group)
                in_group_uid = 'USERS'
                for user in group_active_user_list:
                    in_group_uid = in_group_uid + ',' + user
                user_queue[uid_group].put(in_group_uid)
                for user in group_active_user_list:
                    user_queue[user].put('JOIN,' + uid_group)
            elif message_received.startswith('QUIT'):
                group_header = message_received.split(',')
                uid_group = group_header[1]
                group_active_user_list.remove(uid_group)
                active_user_list.append(uid_group)
                for user in group_active_user_list:
                    user_queue[user].put('QUIT,' + uid_group)
            elif message_received.startswith('GROUP'):
                for user in group_active_user_list:
                    user_queue[user].put(message_received)
            elif message_received.startswith('EMOJI'):
                if self.contact is not None:
                    message_emoji = '\n->' + 'Receive emoji from ' + self.uid\
                                    + ', send to ' + self.contact + ' at ' + ctime() + '\n'
                    user_queue[self.contact].put(message_emoji)
                    user_queue[self.contact].put(message_received)
            elif message_received.startswith('MESSAGE'):
                if self.contact is not None:
                    message_header = message_received.split(',')
                    message_to_send = '\n->' + 'Receive from ' + self.uid + ', send to '\
                                      + self.contact + ' at ' + ctime() + '\n'\
                                      + message_header[1] + '\n'
                    user_queue[self.contact].put(message_to_send)
                else:
                    server_message = '\nCONTACT NEED TO CHOOSE!\n'
                    self.socket.send(server_message.encode('utf-8'))


def main():
    thread_send = threading.Thread(target=send)
    thread_send.daemon = True
    thread_send.start()
    while True:
        new_tcp_socket, new_addr = tcp_socket.accept()
        print('connected from ', new_addr, ctime())
        thread_recv = threading.Thread(target=recv, args=(new_tcp_socket, ))
        thread_recv.daemon = True
        thread_recv.start()


if __name__ == '__main__':
    main()
