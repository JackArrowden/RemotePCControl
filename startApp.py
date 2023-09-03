import tkinter as tk
import socket

class StartApp:
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
        self.root.geometry('250x80')
        self.root.title("Start app")
        
        default_text = "Enter application's name..."

        self.txtID = tk.Entry(self.root, fg = "gray", width = 30, justify = "center", bg = "white", highlightbackground = "#2F4F4F")
        self.txtID.insert(0, default_text)
        self.txtID.pack(pady = (10, 5))
        
        self.txtID.bind("<FocusIn>", on_entry_click)
        self.txtID.bind("<FocusOut>", on_entry_focus_out) 

        self.butInput = tk.Button(self.root, text = "Start", command = self.send_start_request, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1)
        self.butInput.pack(pady = (5, 10))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

    def send_start_request(self):
        name = self.txtID.get()
        appName = name if name.endswith(".exe") else name + ".exe"
        
        self.client.client_socket.sendall("STARTID".encode())
        self.client.client_socket.sendall(appName.encode())
        response = self.client.client_socket.recv(64).decode()
        tk.messagebox.showinfo("Start Result", response)

    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()