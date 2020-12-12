import time
import _thread
import Files
from socket import *
from tkinter import *
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

        self.frame1 = Frame(self.root, bd=18)
        self.frame1.grid(row=0, column=0)

        self.frame2 = Frame(self.frame1)
        self.frame2.grid(row=0, column=0)

        self.label4 = Label(self.frame1, text='Please connect first.')
        self.label4.grid(row=1, column=0, pady=10)

        self.frame4 = Frame(self.frame1, bd=10)
        self.frame4.grid(row=2, column=0)

        self.frame3 = Frame(self.frame2, bd=5)
        self.frame3.grid(row=0, column=0)

        self.label1 = Label(self.frame3, text='IP', width=8)
        self.label1.grid(row=0, column=0)
        self.entry1 = Entry(self.frame3, width=15)
        self.entry1.insert(0, '127.0.0.1')
        self.entry1.grid(row=0, column=1)
        self.label2 = Label(self.frame3, text='PORT', width=8)
        self.label2.grid(row=1, column=0)
        self.entry2 = Entry(self.frame3, width=15)
        self.entry2.insert(0, '12000')
        self.entry2.grid(row=1, column=1)

        self.button1 = Button(self.frame2, text='CONNECT', height=2, width=15, command=self.connect)
        self.button1.grid(row=0, column=1, padx=5)

        self.label3 = Label(self.frame4, text='UID', width=8)
        self.label3.grid(row=0, column=0, pady=5)
        self.entry3 = Entry(self.frame4, width=20)
        self.entry3.insert(0, '123456')
        self.entry3.grid(row=0, column=1, pady=5)

        self.button2 = Button(self.frame1, text='LOG IN/REGISTER', width=30, command=self.login)
        self.button2.grid(row=3, column=0)

        self.label5 = Label(self.frame1, text='Please insert UID, new UIDs '
                                              'will be automatically registered.')
        self.label5.grid(row=4, column=0, pady=15)

        self.root.mainloop()

    def message(self):
        self.root = Tk()
        self.root.title('Chatting')
        self.frame1 = Frame(self.root, bd=10)
        self.frame1.grid(row=0, column=0)

        self.frame2 = Frame(self.frame1)
        self.frame2.grid(row=0, column=0)
        self.frame3 = Frame(self.frame1)
        self.frame3.grid(row=0, column=1, padx=15)

        self.text1 = Text(self.frame2, height=20, width=54, wrap=WORD)
        self.text1.grid(row=0, column=0, columnspan=2)
        self.scrollbar1 = Scrollbar(self.frame2, width=20)
        self.scrollbar1.grid(row=0, column=2)
        self.scrollbar1.config(command=self.text1.yview)

        self.entry1 = Entry(self.frame2, width=44)
        self.entry1.grid(row=1, column=0, pady=10)
        self.button1 = Button(self.frame2, width=8, text='SEND', command=self.send)
        self.button1.grid(row=1, column=1, pady=10)

        self.label1 = Label(self.frame2, text='Click Browse and select a file to send ')
        self.label1.grid(row=2, column=0, pady=10, stick=W)
        self.button2 = Button(self.frame2, width=8, text='Browse', command=self.send_file)
        self.button2.grid(row=2, column=1, pady=10)

        self.label2 = Label(self.frame3, width=14, text='UID:' + self.uid_me)
        self.label2.grid(row=1, column=0)
        self.button3 = Button(self.frame3, text='LOG OUT', width=8, command=self.logout)
        self.button3.grid(row=1, column=1)

        self.label3 = Label(self.frame3, text='Contacts', bd=5)
        self.label3.grid(row=2, column=0, columnspan=2)

        self.listbox1 = Listbox(self.frame3, height=14, width=24)
        self.listbox1.insert(END, '000000')
        self.listbox1.grid(row=3, column=0, columnspan=2)
        self.scrollbar2 = Scrollbar(self.frame3, width=20)
        self.scrollbar2.grid(row=3, column=2)
        self.scrollbar2.config(command=self.listbox1.yview)

        self.button4 = Button(self.frame3, width=23, text='Contact', command=self.contact)
        self.button4.grid(row=4, column=0, columnspan=2, pady=12)

        self.entry3 = Entry(self.frame3, width=14)
        self.entry3.grid(row=5, column=0)
        self.button5 = Button(self.frame3, width=8, text='Insert', command=self.insert)
        self.button5.grid(row=5, column=1)

        _thread.start_new_thread(self.receiving, ())
        _thread.start_new_thread(self.recv, ())

        self.root.mainloop()

    def connect(self):
        ip = self.entry1.get()
        port = self.entry2.get()
        addr = (ip, int(port))
        try:
            self.tcp_socket.connect(addr)
        except timeout:
            messagebox.showerror('Error', 'Cannot connect server!')
        else:
            messagebox.showinfo('Success', 'Successfully connected!')

    def login(self):
        self.uid_me = self.entry3.get()
        if self.uid_me.isdigit():
            self.tcp_socket.send(self.uid_me.encode('utf-8'))
            self.root.destroy()
            self.message()

    def logout(self):
        self.tcp_socket.send('LOG OUT'.encode('utf-8'))
        self.root.destroy()
        self.default()

    def insert(self):
        uid_new = self.entry3.get()
        if uid_new.isdigit():
            self.listbox1.insert(END, uid_new)

    def contact(self):
        self.uid_chat = self.listbox1.get(self.listbox1.curselection())
        self.tcp_socket.send(self.uid_chat.encode())
        self.text1.insert(END, '\n->Now try to contact UID '+self.uid_chat+' at '+ctime()+'\n')
        self.text1.see(END)

    def send(self):
        message_to_send = '!' + self.entry1.get()
        self.entry1.delete(0, END)
        if message_to_send:
            self.tcp_socket.send(message_to_send.encode())
            self.text1.insert(END, '\n->' + self.uid_me + ' send to '
                              + self.uid_chat + ' at ' + ctime() + '\n')
            self.text1.insert(END, message_to_send[1:] + '\n')
            self.text1.see(END)

    def recv(self):
        while 1:
            # time.sleep(1)
            if self.queue.empty() is False:
                message_to_recv = self.queue.get()
                self.text1.insert(END, message_to_recv)
                self.text1.see(END)

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
                    #         print(recv_size, '/', file_size)
                    # return file_size, file_name
                else:
                    self.queue.put(message_received)
            except timeout:
                pass

    def send_file(self):
        self.file_name = askopenfilename()
        if os.path.isfile(self.file_name):
            Files.client_send(self.tcp_socket, self.file_name)
            self.text1.insert(END, '\n->' + self.uid_me + ' send file:\n\n' + self.file_name
                              + '\n\n->to ' + self.uid_chat + ' at ' + ctime() + '\n')
            self.text1.see(END)

def main():
    init = Init()
    init.default()


if __name__ == '__main__':
    main()