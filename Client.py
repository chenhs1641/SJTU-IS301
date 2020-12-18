import threading
import time
from queue import Queue
from socket import *
from tkinter import messagebox
from tkinter.filedialog import *
from time import ctime

BUFSIZE = 1024


class Init(object):
    def __init__(self):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.settimeout(2)
        self.queue = Queue()
        self.group_queue = Queue()

    def default(self):
        self.root = Tk()
        self.root.title('Welcome to Chatting Room!')

        self.frame_all = Frame(self.root, bd=18)
        self.frame_all.grid(row=0, column=0)

        self.frame_connect = Frame(self.frame_all)
        self.frame_connect.grid(row=0, column=0)
        self.label_connect = Label(self.frame_all, text='Please connect first.')
        self.label_connect.grid(row=1, column=0, pady=10)
        self.frame_addr = Frame(self.frame_connect, bd=5)
        self.frame_addr.grid(row=0, column=0)
        self.button_connect = Button(self.frame_connect, text='CONNECT',
                                     height=2, width=15, command=self.connect)
        self.button_connect.grid(row=0, column=1, padx=5)

        self.label_ip = Label(self.frame_addr, text='IP', width=8)
        self.label_ip.grid(row=0, column=0)
        self.entry_ip = Entry(self.frame_addr, width=15)
        self.entry_ip.insert(0, '127.0.0.1')
        self.entry_ip.grid(row=0, column=1)
        self.label_port = Label(self.frame_addr, text='PORT', width=8)
        self.label_port.grid(row=1, column=0)
        self.entry_port = Entry(self.frame_addr, width=15)
        self.entry_port.insert(0, '12000')
        self.entry_port.grid(row=1, column=1)

        self.frame_uid = Frame(self.frame_all, bd=10)
        self.frame_uid.grid(row=2, column=0)
        self.label_uid = Label(self.frame_uid, text='UID', width=8)
        self.label_uid.grid(row=0, column=0, pady=5)
        self.entry_uid = Entry(self.frame_uid, width=20)
        self.entry_uid.insert(0, '1')
        self.entry_uid.grid(row=0, column=1, pady=5)

        self.button_login = Button(self.frame_all, text='LOG IN/REGISTER', width=30,
                                   command=self.login)
        self.button_login.grid(row=3, column=0)
        self.label_login = Label(self.frame_all, text='Please insert UID, new UIDs '
                                                      'will be automatically registered.')
        self.label_login.grid(row=4, column=0, pady=15)

        self.root.mainloop()

    def message(self):
        self.root = Tk()
        self.root.title('Chatting')
        self.frame_all = Frame(self.root, bd=10)
        self.frame_all.grid(row=0, column=0)

        self.emoji_angry = PhotoImage(file='./emoji/angry.png')
        self.emoji_excited = PhotoImage(file='./emoji/excited.png')

        self.frame_left = Frame(self.frame_all)
        self.frame_left.grid(row=0, column=0)
        self.frame_right = Frame(self.frame_all)
        self.frame_right.grid(row=0, column=1, padx=15)

        self.text_message = Text(self.frame_left, height=25, width=54, wrap=WORD)
        self.text_message.grid(row=0, column=0, columnspan=2)
        self.scrollbar_message = Scrollbar(self.frame_left, width=20)
        self.scrollbar_message.grid(row=0, column=2)
        self.scrollbar_message.config(command=self.text_message.yview)

        self.entry_send = Entry(self.frame_left, width=44)
        self.entry_send.grid(row=1, column=0, pady=10)
        self.button_send = Button(self.frame_left, width=8, text='SEND', command=self.send)
        self.button_send.grid(row=1, column=1, pady=10)

        self.frame_function = Frame(self.frame_left)
        self.frame_function.grid(row=2, column=0, columnspan=2)
        self.button_sendfile = Button(self.frame_function, width=10, text='Send a file',
                                      command=self.send_file)
        self.button_sendfile.grid(row=0, column=0)
        self.button_groupchat = Button(self.frame_function, width=10, text='Group chat',
                                       command=self.group_chat)
        self.button_groupchat.grid(row=0, column=1)
        self.button_sendemoji = Button(self.frame_function, width=10, text='Emoji',
                                   command=self.send_emoji)
        self.button_sendemoji.grid(row=0, column=2)

        self.label_uid = Label(self.frame_right, width=14, text='UID:' + self.uid_me)
        self.label_uid.grid(row=1, column=0)
        self.button_logout = Button(self.frame_right, text='LOG OUT', width=8,
                                    command=self.logout)
        self.button_logout.grid(row=1, column=1)

        self.label_contacts = Label(self.frame_right, text='Contacts', bd=5)
        self.label_contacts.grid(row=2, column=0, columnspan=2)
        self.listbox_contacts = Listbox(self.frame_right, height=14, width=24)
        self.listbox_contacts.insert(END, '1')
        self.listbox_contacts.grid(row=3, column=0, columnspan=2)
        self.scrollbar_contacts = Scrollbar(self.frame_right, width=20)
        self.scrollbar_contacts.grid(row=3, column=2)
        self.scrollbar_contacts.config(command=self.listbox_contacts.yview)

        self.button_contact = Button(self.frame_right, width=23, text='Contact',
                                     command=self.contact)
        self.button_contact.grid(row=4, column=0, columnspan=2, pady=18)

        self.entry_insert = Entry(self.frame_right, width=14)
        self.entry_insert.grid(row=5, column=0)
        self.button_insert = Button(self.frame_right, width=8, text='Insert',
                                    command=self.insert)
        self.button_insert.grid(row=5, column=1)

        thread_receiving = threading.Thread(target=self.receiving)
        thread_recv = threading.Thread(target=self.recv)
        thread_receiving.daemon = True
        thread_recv.daemon = True
        thread_receiving.start()
        thread_recv.start()

        self.root.mainloop()

    def group_chat(self):
        self.root.withdraw()
        self.group_root = Tk()
        self.group_root.title('Group chat')

        self.frame_group = Frame(self.group_root, bd=15)
        self.frame_group.grid(row=0, column=0)
        self.frame_group_left = Frame(self.frame_group)
        self.frame_group_left.grid(row=0, column=0)
        self.frame_group_right = Frame(self.frame_group)
        self.frame_group_right.grid(row=0, column=1, padx=10)

        self.text_group = Text(self.frame_group_left, height=25, width=54, wrap=WORD)
        self.text_group.grid(row=0, column=0, columnspan=2)
        self.scrollbar_group = Scrollbar(self.frame_group_left, width=20)
        self.scrollbar_group.grid(row=0, column=2)
        self.scrollbar_group.config(command=self.text_group.yview)

        self.entry_group = Entry(self.frame_group_left, width=44)
        self.entry_group.grid(row=1, column=0, pady=10)
        self.button_send_group = Button(self.frame_group_left, width=8, text='Send',
                                        command=self.send_group)
        self.button_send_group.grid(row=1, column=1, pady=10)

        self.label_users = Label(self.frame_group_right, text='Online users', bd=8)
        self.label_users.grid(row=0, column=0)
        self.listbox_users = Listbox(self.frame_group_right, height=16, width=24)
        self.listbox_users.grid(row=1, column=0)
        self.scrollbar_users = Scrollbar(self.frame_group_right, width=20)
        self.scrollbar_users.grid(row=1, column=1)
        self.scrollbar_users.config(command=self.listbox_users.yview)
        self.button_quit = Button(self.frame_group_right, width=8, text='Quit',
                                  command=self.quit)
        self.button_quit.grid(row=2, column=0, pady=10)

        send_server = 'JOIN,' + self.uid_me
        self.tcp_socket.send(send_server.encode('utf-8'))

        thread_recv_group = threading.Thread(target=self.recv_group)
        thread_recv_group.daemon = True
        thread_recv_group.start()

        self.group_root.mainloop()

    def connect(self):
        ip = self.entry_ip.get()
        port = self.entry_port.get()
        addr = (ip, int(port))
        try:
            self.tcp_socket.connect(addr)
        except timeout:
            messagebox.showerror('Error', 'Cannot connect server!')
        else:
            messagebox.showinfo('Success', 'Successfully connected!')

    def login(self):
        self.uid_me = self.entry_uid.get()
        if self.uid_me.isdigit():
            self.tcp_socket.send(self.uid_me.encode('utf-8'))
            self.root.destroy()
            self.message()

    def logout(self):
        self.tcp_socket.send('LOG OUT'.encode('utf-8'))
        self.root.destroy()
        self.default()

    def insert(self):
        uid_new = self.entry_insert.get()
        if uid_new.isdigit():
            self.listbox_contacts.insert(END, uid_new)

    def contact(self):
        self.uid_chat = self.listbox_contacts.get(self.listbox_contacts.curselection())
        self.tcp_socket.send(self.uid_chat.encode())
        self.text_message.insert(END, '\n->Now try to contact UID ' + self.uid_chat
                                 + ' at ' + ctime() + '\n')
        self.text_message.see(END)

    def send(self):
        if self.entry_send.get():
            message_to_send = 'MESSAGE,' + self.entry_send.get()
            self.entry_send.delete(0, END)
            self.tcp_socket.send(message_to_send.encode())
            self.text_message.insert(END, '\n->' + self.uid_me + ' send to '
                                     + self.uid_chat + ' at ' + ctime() + '\n')
            self.text_message.insert(END, message_to_send[9:] + '\n')
            self.text_message.see(END)

    def send_file(self):
        send_file_name = askopenfilename()
        if os.path.isfile(send_file_name):
            if not os.path.isfile(send_file_name):
                print('file:', send_file_name, ' is not exists')
                return
            else:
                send_file_size = os.path.getsize(send_file_name)
                file_name = send_file_name.split('/')[-1]
                header = 'FILE' + ',' + file_name + ',' + str(send_file_size)
                self.tcp_socket.send(header.encode('utf-8'))
                time.sleep(0.1)
                with open(send_file_name, 'rb') as f:
                    for line in f:
                        self.tcp_socket.send(line)
                time.sleep(0.1)
            self.text_message.insert(END, '\n->' + self.uid_me + ' send file:\n\n'
                                     + send_file_name + '\n\n->to ' + self.uid_chat
                                     + ' at ' + ctime() + '\n')
            self.text_message.see(END)

    def send_group(self):
        if self.entry_group.get():
            message_group = 'GROUP,' + self.uid_me + ',' + 'send at ' + ctime() +\
                            ':\n' + self.entry_group.get()
            self.entry_group.delete(0, END)
            self.tcp_socket.send(message_group.encode('utf-8'))

    def send_emoji(self):
        self.emoji_root = Toplevel()
        self.emoji_root.title('Please select emoji to send.')

        self.frame_emoji = Frame(self.emoji_root, bd=30)
        self.frame_emoji.grid(row=0, column=0)
        self.button_angry = Button(self.frame_emoji, command=self.send_emoji_angry,
                                   image=self.emoji_angry, relief=FLAT, bd=0)
        self.button_excited = Button(self.frame_emoji, command=self.send_emoji_excited,
                                     image=self.emoji_excited, relief=FLAT, bd=0)
        self.button_angry.grid(row=0, column=0, padx=30)
        self.button_excited.grid(row=0, column=1, padx=30)

        self.emoji_root.mainloop()

    def send_emoji_angry(self):
        self.tcp_socket.send('EMOJI,ANGRY'.encode('utf-8'))
        self.text_message.insert(END, '\n->' + self.uid_me + ' send emoji to '
                                 + self.uid_chat + ' at ' + ctime() + '\n')
        self.text_message.image_create(END, image=self.emoji_angry)
        self.text_message.insert(END, '\n')
        self.emoji_root.destroy()

    def send_emoji_excited(self):
        self.tcp_socket.send('EMOJI,EXCITED'.encode('utf-8'))
        self.text_message.insert(END, '\n->' + self.uid_me + ' send emoji to '
                                 + self.uid_chat + ' at ' + ctime() + '\n')
        self.text_message.image_create(END, image=self.emoji_excited)
        self.text_message.insert(END, '\n')
        self.emoji_root.destroy()

    def receiving(self):
        while 1:
            try:
                message_received = self.tcp_socket.recv(BUFSIZE).decode('utf-8')
                if message_received == 'REPEAT LOGIN':
                    messagebox.showerror('Error', 'Repeat login!')
                    self.root.destroy()
                elif message_received.startswith('FILE'):
                    # HINT TO SAVE FILE!
                    message_header = message_received.split(',')
                    message_received = self.tcp_socket.recv(BUFSIZE).decode('utf-8')
                    self.queue.put(message_received)
                    messagebox.showinfo("Info", "Someone wants to send a file to you.\n"
                                                "Please choose a path to save.")
                    self.tcp_socket.send("CONFIRM".encode('utf-8'))
                    file_path = askdirectory()
                    file_size = int(message_header[2])
                    file_name = message_header[1]
                    with open(file_path + '/' + file_name, 'wb') as f:
                        recv_size = 0
                        while recv_size < file_size:
                            line = self.tcp_socket.recv(BUFSIZE)
                            f.write(line)
                            recv_size += len(line)
                    self.queue.put("\n->You have successfully received the file!\n")
                elif message_received.startswith('USERS'):
                    online_list = message_received.split(',')
                    for user in online_list:
                        if user != 'USERS':
                            while 1:
                                try:
                                    self.listbox_users.insert(END, user)
                                    break
                                except timeout:
                                    pass
                elif message_received.startswith('JOIN'):
                    message = message_received.split(',')
                    join_uid = message[1]
                    self.group_queue.put('\n->UID: ' + join_uid + ' has joined group chat.\n')
                    if self.uid_me != join_uid:
                        self.listbox_users.insert(END, join_uid)
                elif message_received.startswith('QUIT'):
                    message = message_received.split(',')
                    quit_uid = message[1]
                    self.group_queue.put('\n->UID: ' + quit_uid + ' has quited group chat.\n')
                    for i in range(0, self.listbox_users.size()):
                        if self.listbox_users.get(i) == quit_uid:
                            self.listbox_users.delete(i)
                            break
                elif message_received.startswith('GROUP'):
                    message = message_received.split(',')
                    speaker_uid = message[1]
                    speak_content = message[2]
                    self.group_queue.put('\n->User UID: ' + speaker_uid + ' ' +
                                         speak_content + '\n')
                elif message_received.startswith('EMOJI'):
                    message = message_received.split(',')
                    emoji_name = message[1]
                    if emoji_name == 'ANGRY':
                        self.text_message.image_create(END, image=self.emoji_angry)
                    elif emoji_name == 'EXCITED':
                        self.text_message.image_create(END, image=self.emoji_excited)
                    self.text_message.insert(END, '\n')
                    self.text_message.see(END)
                else:
                    self.queue.put(message_received)
            except timeout:
                pass

    def recv(self):
        while 1:
            if self.queue.empty() is False:
                message_to_recv = self.queue.get()
                self.text_message.insert(END, message_to_recv)
                self.text_message.see(END)

    def recv_group(self):
        while 1:
            if self.group_queue.empty() is False:
                message_to_recv = self.group_queue.get()
                self.text_group.insert(END, message_to_recv)
                self.text_group.see(END)

    def quit(self):
        quit_message = 'QUIT,' + self.uid_me
        self.tcp_socket.send(quit_message.encode('utf-8'))
        self.group_root.destroy()
        self.root.deiconify()
        # stop thread!!!


def main():
    init = Init()
    init.default()


if __name__ == '__main__':
    main()
