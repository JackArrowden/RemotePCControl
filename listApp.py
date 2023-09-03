import socket
import tkinter as tk
from tkinter import ttk
from kill import KillProcess
from startApp import StartApp
import struct

class listApp:
    def __init__(self, client, client_socket):
        self.client = client
        self.client.client_socket = client_socket        

        self.root = tk.Tk()
        self.root.geometry('400x289')
        self.root.title("ListApp Window")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady = 10)

        self.button1 = tk.Button(self.button_frame, text = "View", command = self.view_apps, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button1.pack(side = tk.LEFT, padx = (10, 5))

        self.button2 = tk.Button(self.button_frame, text = "Kill", command = self.kill_app, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button2.pack(side = tk.LEFT, padx = (5, 5))

        self.button3 = tk.Button(self.button_frame, text = "Start", command = self.start_app, bg = "#323232", fg = "#FAFAFA", width = 8)
        self.button3.pack(side = tk.LEFT, padx = (5, 5))

        self.button4 = tk.Button(self.button_frame, text = "Clear", command = self.clear_list, bg = "#323232", fg = "#FAFAFA", width = 8)
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

    def view_apps(self):
        self.client.client_socket.sendall("VIEW".encode())
        temp = self.client.client_socket.recv(8)
        numApps = struct.unpack('!Q', temp)[0]

        for _ in range(numApps):
            lenEncode = self.client.client_socket.recv(8)
            lenAppName = struct.unpack('!Q', lenEncode)[0]
            appNameEncoded = self.client.client_socket.recv(lenAppName)
            
            lenIDEncode = self.client.client_socket.recv(8)
            lenAppID = struct.unpack('!Q', lenIDEncode)[0]
            appIDEncoded = self.client.client_socket.recv(lenAppID)
            
            lenThreadsEncode = self.client.client_socket.recv(8)
            lenNumThreads = struct.unpack('!Q', lenThreadsEncode)[0]    
            appNumThreadsEncoded = self.client.client_socket.recv(lenNumThreads)            
            
            appName = appNameEncoded.decode()
            appID = appIDEncoded.decode()
            appNumThreads = appNumThreadsEncoded.decode()
            self.tree.insert("", "end", values = (appName, appID, appNumThreads))

    def kill_app(self):
        self.client.client_socket.sendall("KILL".encode())
        kill_app = KillProcess(self.client, self.client.client_socket)

    def start_app(self):
        self.client.client_socket.sendall("START".encode())
        start_app = StartApp(self.client, self.client.client_socket)

    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        
    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()