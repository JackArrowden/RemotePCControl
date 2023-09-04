import socket
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import struct
import datetime

class screenCaptureWindow:
    def __init__(self, client, client_socket):
        self.client = client
        self.client.client_socket = client_socket
    
    def request_screenshot(self):
        s = "TAKE"
        self.client.client_socket.sendall(s.encode())
        byteRecv = self.client.client_socket.recv(1024)
        width_byte = self.client.client_socket.recv(1024)
        height_byte = self.client.client_socket.recv(1024)
        length = struct.unpack('!Q', byteRecv)[0]
        imageData = b""
        remaining_data = length
        while remaining_data > 0:
            chunk = self.client.client_socket.recv(min(remaining_data, 1024))
            if not chunk:
                break
            imageData += chunk
            remaining_data -= len(chunk)
        
        width = struct.unpack('!I', width_byte)[0]
        height = struct.unpack('!I', height_byte)[0]
        screenshot = Image.frombytes("RGB", (width, height), imageData)
        screenshot.show()
        screenshot.save(datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + ".png", format = "PNG")
        
    def on_closing(self):
        self.client.client_socket.sendall("QUIT".encode())
