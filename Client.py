import _thread
import Files
from socket import *
from tkinter import messagebox
from tkinter.filedialog import *
from time import ctime
from queue import Queue

BUFSIZE = 1024


class Init(object):
    def __init__(self):
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.settimeout(2)
        self.queue = Queue()

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

        self.label_uid = Label(self.frame_right, width=14, text='UID:' + self.uid_me)
        self.label_uid.grid(row=1, column=0)
        self.button_logout = Button(self.frame_right, text='LOG OUT', width=8, command=self.logout)
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

        _thread.start_new_thread(self.receiving, ())
        _thread.start_new_thread(self.recv, ())

        self.root.mainloop()

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
        message_to_send = '!' + self.entry_send.get()
        self.entry_send.delete(0, END)
        if message_to_send:
            self.tcp_socket.send(message_to_send.encode())
            self.text_message.insert(END, '\n->' + self.uid_me + ' send to '
                                     + self.uid_chat + ' at ' + ctime() + '\n')
            self.text_message.insert(END, message_to_send[1:] + '\n')
            self.text_message.see(END)

    def recv(self):
        while 1:
            if self.queue.empty() is False:
                message_to_recv = self.queue.get()
                self.text_message.insert(END, message_to_recv)
                self.text_message.see(END)

    def receiving(self):
        while 1:
            # time.sleep(0.1)
            try:
                message_received = self.tcp_socket.recv(BUFSIZE).decode('utf-8')
                # print(message_received)
                if message_received.startswith('FILE'):
                    # HINT TO SAVE FILE!
                    message_header = message_received.split(',')
                    message_received = self.tcp_socket.recv(BUFSIZE).decode('utf-8')
                    self.queue.put(message_received)
                    # print(self.tcp_socket)
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
                else:
                    self.queue.put(message_received)
            except timeout:
                pass

    def send_file(self):
        self.file_name = askopenfilename()
        if os.path.isfile(self.file_name):
            Files.client_send(self.tcp_socket, self.file_name)
            self.text_message.insert(END, '\n->' + self.uid_me + ' send file:\n\n'
                                     + self.file_name + '\n\n->to ' + self.uid_chat
                                     + ' at ' + ctime() + '\n')
            self.text_message.see(END)


def main():
    init = Init()
    init.default()


if __name__ == '__main__':
    main()
