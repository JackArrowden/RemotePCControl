import tkinter as tk
import socket
from keylog import KeylogWindow
from pic import screenCaptureWindow
from app import listApp
from process import listProcess

class ClientApp:
    def __init__(self, root):
        def on_entry_click(event):
            if root.entry.get() == default_text:
                root.entry.delete(0, tk.END)
                root.entry.config(fg="black")

        def on_entry_focus_out(event):
            if root.entry.get() == "":
                root.entry.insert(0, default_text)
                root.entry.config(fg="gray")

        self.root = root
        self.root.geometry('310x260')
        self.root.title("Client Application")
        
        default_text = "Enter server's IP address..."

        root.entry = tk.Entry(root, fg = "gray", width = 30, justify = "center", bg = "white", highlightbackground = "#2F4F4F")
        root.entry.insert(0, default_text)
        root.entry.pack(pady = (10, 5))

        root.entry.bind("<FocusIn>", on_entry_click)
        root.entry.bind("<FocusOut>", on_entry_focus_out)  

        self.connect_button = tk.Button(root, text = "Connect", command = self.connect_to_server, bg = "#323232", fg = "#FAFAFA", width = 10, height = 1, cursor = "hand2")
        self.connect_button.pack(pady = (5, 10))

        ### Frame 1
        self.button_frame1 = tk.Frame(self.root)
        self.button_frame1.pack(pady = (10, 5))

        self.app_button = tk.Button(self.button_frame1, text = "App running", command = self.open_application, bg = "#323232", fg = "#FAFAFA", width = 19, height = 1, cursor = "hand2")
        self.app_button.pack(side = tk.LEFT, padx = (10, 5))
        
        self.process_button = tk.Button(self.button_frame1, text = "Process running", command = self.list_processes, bg = "#323232", fg = "#FAFAFA", width = 14, height = 1, cursor = "hand2")
        self.process_button.pack(side = tk.LEFT, padx = (5, 10))

        ### Frame 2
        self.button_frame2 = tk.Frame(self.root)
        self.button_frame2.pack(pady = (5, 10))
        
        ## Frame 2 left
        self.button_frame2_left = tk.Frame(self.button_frame2)
        self.button_frame2_left.pack(side = tk.LEFT, padx = (10, 5))

        # Frame 2 top left
        self.button_frame2_top_left = tk.Frame(self.button_frame2_left)
        self.button_frame2_top_left.pack(pady = (0, 5))

        self.shutdown_button = tk.Button(self.button_frame2_top_left, text = "Shutdown server", command = self.shutdown_server, bg = "#323232", fg = "#FAFAFA", width = 8, height = 5, wraplength = 70, cursor = "hand2")
        self.shutdown_button.pack(side = tk.LEFT, padx = (0, 5))

        self.pic_button = tk.Button(self.button_frame2_top_left, text = "Screen capture", command = self.take_picture, bg = "#323232", fg = "#FAFAFA", width = 8, height = 5, wraplength = 70, cursor = "hand2")
        self.pic_button.pack(side = tk.LEFT, padx = (5, 0))

        self.keylog_button = tk.Button(self.button_frame2_left, text = "Keystroke", command = self.start_keylogging, bg = "#323232", fg = "#FAFAFA", width = 19, height = 1, cursor = "hand2")
        self.keylog_button.pack(pady = (5, 0))

        ## Frame 2 right
        self.exit_button = tk.Button(self.button_frame2, text = "Exit", command = self.close_connection, bg = "#323232", fg = "#FAFAFA", width = 14, height = 7, cursor = "hand2")
        self.exit_button.pack(padx = (5, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.close_connection)

        self.client_socket = None
        self.connect_status = False

    def connect_to_server(self):
        try:
            ip_address = self.root.entry.get()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip_address, 32123))
            self.connect_status = True
            tk.messagebox.showinfo("Connected", "Connected to the server successfully!")
        except Exception as e:
            tk.messagebox.showerror("Connection Error", "Failed to connect to the server.")

    def open_application(self):
        if not self.connect_status:
            tk.messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.client_socket.sendall("APPLICATION".encode())
        listOfApp = listApp(self, self.client_socket)

    def shutdown_server(self):
        if not self.connect_status:
            tk.messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.client_socket.sendall("SHUTDOWN".encode())
        self.client_socket.close()
        tk.messagebox.showinfo("Server Shutdown", "Server has been shut down.")

    def close_connection(self):
        if self.client_socket:
            self.client_socket.sendall("QUIT".encode())
            self.client_socket.close()

        self.root.destroy()

    def take_picture(self):
        if not self.connect_status:
            tk.messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.client_socket.sendall("TAKEPIC".encode())
        screenCapture = screenCaptureWindow(self, self.client_socket)
        screenCapture.request_screenshot()
        screenCapture.on_closing()

    def start_keylogging(self):
        if not self.connect_status:
            tk.messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.client_socket.sendall("KEYLOG".encode())
        keyLog = KeylogWindow(self, self.client_socket)

    def list_processes(self):
        if not self.connect_status:
            tk.messagebox.showerror("Connection Error", "Not connected to the server.")
            return

        self.client_socket.sendall("PROCESS".encode())
        listOfProcess = listProcess(self, self.client_socket)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
