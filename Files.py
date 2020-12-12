import os
import time

BUFSIZE = 1024


def client_send(client_sendfile_socket, send_file_name):
    if not os.path.isfile(send_file_name):
        print('file:', send_file_name, ' is not exists')
        return
    else:
        send_file_size = os.path.getsize(send_file_name)
        file_name = send_file_name.split('/')[-1]
        header = 'FILE' + ',' + file_name + ',' + str(send_file_size)
        client_sendfile_socket.send(header.encode('utf-8'))
        time.sleep(0.1)
        with open(send_file_name, 'rb') as f:
            for line in f:
                client_sendfile_socket.send(line)
        time.sleep(0.1)


def server_recv(server_recvfile_socket, message_received):
    message_header = message_received.split(',')
    file_size = int(message_header[2])
    file_name = message_header[1]
    with open('./' + file_name, 'wb') as f:
        recv_size = 0
        while recv_size < file_size:
            line = server_recvfile_socket.recv(BUFSIZE)
            f.write(line)
            recv_size += len(line)
            # print(recv_size, '/', file_size)
    return file_size, file_name
