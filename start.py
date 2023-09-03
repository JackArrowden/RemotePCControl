import tkinter as tk
from tkinter import ttk
import socket
import struct

class StartProcess:
    def __init__(self, client, client_socket):
        def on_entry_click(event):
            if self.txtID.get() == default_text:
                self.txtID.delete(0, tk.END)
                self.txtID.config(fg = "black")

        def on_entry_focus_out(event):
            if self.txtID.get() == "":
                self.txtID.insert(0, default_text)
                self.txtID.config(fg = "gray")

        self.client = client
        self.client.client_socket = client_socket  
        
        self.root = tk.Tk()
        self.root.geometry('400x288')
        self.root.title("Start process")
        
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady = 10)
        
        default_text = "Enter the index of process..."

        self.txtID = tk.Entry(self.button_frame, fg = "gray", width = 30, justify = "center", bg = "white", highlightbackground = "#2F4F4F")
        self.txtID.insert(0, default_text)
        self.txtID.pack(side = tk.LEFT, padx = (10, 5))
        
        self.txtID.bind("<FocusIn>", on_entry_click)
        self.txtID.bind("<FocusOut>", on_entry_focus_out) 

        self.butInput = tk.Button(self.button_frame, text = "Start", command = self.send_start_request, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1)
        self.butInput.pack(side = tk.LEFT, padx = (5, 10))
        
        self.tree = ttk.Treeview(self.root, columns = ("No.", "Name"), show = "headings")
        self.tree.heading("No.", text = "Index")
        self.tree.heading("Name", text = "Name")
  
        self.tree.pack(padx = 10)
        
        self.tree.column("No.", width = 80)
        self.tree.column("Name", width = 280)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        temp = self.client.client_socket.recv(8)
        self.numApps = struct.unpack('!Q', temp)[0]
        self.listApps = []
        
        for i in range(self.numApps):
            lenAppEncode = self.client.client_socket.recv(2)
            lenAppName = struct.unpack('!H', lenAppEncode)[0]
            appNameEncoded = self.client.client_socket.recv(lenAppName)
            lenDirEncode = self.client.client_socket.recv(2)
            lenDirName = struct.unpack('!H', lenDirEncode)[0]
            dirNameEncoded = self.client.client_socket.recv(lenDirName)
            
            appName = appNameEncoded.decode()
            dirName = dirNameEncoded.decode()
            
            self.listApps.append(dirName)
            self.tree.insert("", "end", values = (i, appName))
        
        self.root.mainloop()

    def send_start_request(self):
        program_id = int(self.txtID.get())
        if program_id >= 0 and program_id < self.numApps:
            dir_program_name = self.listApps[program_id]
            self.client.client_socket.sendall("STARTID".encode())
            self.client.client_socket.sendall(dir_program_name.encode())
            response = self.client.client_socket.recv(64).decode()
            tk.messagebox.showinfo("Start Result", response)
        else:
            response = "Invalid ID"
            tk.messagebox.showinfo("Start Result", response)

    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()