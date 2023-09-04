import socket
import tkinter as tk
from tkinter import ttk
from kill import KillProcess
from startProcess import StartProcess
import struct

class listProcess:
    def __init__(self, client, client_socket):
        self.client = client
        self.client.client_socket = client_socket        

        self.root = tk.Tk()
        self.root.geometry('400x289')
        self.root.title("ListProcesses Window")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady = 10)

        self.button1 = tk.Button(self.button_frame, text = "View", command = self.view_processes, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button1.pack(side = tk.LEFT, padx = (10, 5))

        self.button2 = tk.Button(self.button_frame, text = "Kill", command = self.kill_processes, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button2.pack(side = tk.LEFT, padx = (5, 5))

        self.button3 = tk.Button(self.button_frame, text = "Start", command = self.start_processes, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button3.pack(side = tk.LEFT, padx = (5, 5))

        self.button4 = tk.Button(self.button_frame, text = "Clear", command = self.clear_processes, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button4.pack(side = tk.LEFT, padx = (5, 10))

        self.tree = ttk.Treeview(self.root, columns = ("Name", "ID", "Threads"), show = "headings")
        self.tree.heading("Name", text = "Name")
        self.tree.heading("ID", text = "ID")
        self.tree.heading("Threads", text = "Threads")
  
        self.tree.pack(padx = 10)
        
        self.tree.column("Name", width = 200)
        self.tree.column("ID", width = 80)
        self.tree.column("Threads", width = 80)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.mainloop()

    def view_processes(self):
        self.client.client_socket.sendall("VIEW".encode())
        temp = self.client.client_socket.recv(8)
        numApps = struct.unpack('!Q', temp)[0]

        for _ in range(numApps):
            lenEncode = self.client.client_socket.recv(2)
            lenProcessName = struct.unpack('!H', lenEncode)[0]
            processNameEncoded = self.client.client_socket.recv(lenProcessName)
            
            processIDEncoded = self.client.client_socket.recv(2)
            processNumThreadsEncoded = self.client.client_socket.recv(2)
            
            processName = processNameEncoded.decode()
            processID = struct.unpack('!H', processIDEncoded)[0]
            processNumThreads = struct.unpack('!H', processNumThreadsEncoded)[0]
            self.tree.insert("", "end", values = (processName, processID, processNumThreads))

    def kill_processes(self):
        self.client.client_socket.sendall("KILL".encode())
        kill_processes = KillProcess(self.client, self.client.client_socket)

    def start_processes(self):
        self.client.client_socket.sendall("START".encode())
        start_processes = StartProcess(self.client, self.client.client_socket)

    def clear_processes(self):
        self.tree.delete(*self.tree.get_children())
        
    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()
