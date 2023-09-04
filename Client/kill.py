import tkinter as tk
import socket

class Kill:
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
        self.root.title("Kill")
        
        default_text = "Enter ID..."

        self.txtID = tk.Entry(self.root, fg = "gray", width = 30, justify = "center", highlightbackground = "#2F4F4F")
        self.txtID.insert(0, default_text)
        self.txtID.pack(pady = (10, 5)) 
               
        self.txtID.bind("<FocusIn>", on_entry_click)
        self.txtID.bind("<FocusOut>", on_entry_focus_out) 

        self.butInput = tk.Button(self.root, text = "Kill", command = self.send_kill_request, bg = "#323232", fg = "#FAFAFA", width = 12)
        self.butInput.pack(pady = (5, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

    def send_kill_request(self):
        program_id = self.txtID.get()
        if program_id:
            self.client.client_socket.sendall("KILLID".encode())
            self.client.client_socket.send(program_id.encode())
            response = self.client.client_socket.recv(64).decode()
            tk.messagebox.showinfo("Kill Result", response)

    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
        self.root.destroy()
