
import threading
import socket
import sys
import traceback
import time
import Globals
import Net.Client as Client


class Server:

    def __init__(self,ip='localhost',port=57201,buffersize=1024,backlog=5,timeout=10):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.TCP_BUFFER_SIZE = buffersize
        self.TCP_BACKLOG = backlog
        self.TCP_TIMEOUT = timeout
        self.clients = []
        self.events = {'close_all':threading.Event()}

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Uncomment for issues with rebinding sockets
        self.server.bind((self.TCP_IP, self.TCP_PORT))
        self.server.listen(self.TCP_BACKLOG)
        self.server.settimeout(self.TCP_TIMEOUT)
        self.server_thread = threading.Thread(target=self.run)
        self.server_thread.setName("TCP Server on {0}:{1}".format(self.TCP_IP,self.TCP_PORT))
        self.server_thread.daemon=True
        self.events['close_all'].clear()
        self.server_thread.start()
        if Globals.INFO['TCP']:
            sys.stdout.write("SERVER_INFO: Listening on {0}:{1}\n".format(self.TCP_IP,self.TCP_PORT))

    def stop(self):
        self.events['close_all'].set()
        if Globals.INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: Disconnecting all clients...\n")
        for c in self.clients:
            c.close()
        for c in self.clients:
            c.closeEvent.wait()
            c.join()
        if Globals.INFO['TCP']:
            sys.stdout.write("SERVER_INFO: Closing server...\n")
        self.server_thread.join()
        self.server.close()
        self.events['close_all'].clear()

    def run(self):
        while True:
            if Globals.DEBUG['TCP']:
                sys.stdout.write('SERVER_DEBUG: Beginning loop\n')
            try:
                c = Client.Client(self.server.accept(),self.TCP_BUFFER_SIZE)
                c.start()
                self.clients.append(c)
            except socket.timeout:
                if Globals.DEBUG['TCP']:
                    sys.stdout.write('SERVER_DEBUG: Socket accept timed out\n')
            except:
                e = sys.exc_info()
                sys.stderr.write('SERVER_ERROR: {0}: {1}\n'.format(e[0],e[1]))
                traceback.print_tb(e[2])
            if self.events['close_all'].isSet():
                break
            time.sleep(0.01)