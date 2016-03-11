
import threading
import sys
import traceback
import json
import Globals


class Client(threading.Thread): # Modified from http://ilab.cs.byu.edu/python/threadingmodule.html
    def __init__(self, client, size):
        threading.Thread.__init__(self)
        self.client = client[0]
        self.address = client[1]
        self.size = size
        self.closeEvent = threading.Event()
        self.jse = json.JSONEncoder()


    def run(self):
        # Look into this code
        try:
            if Globals.INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: New client {0}\n".format(self.address))
            while True:
                data = self.client.recv(self.size)
                if data:
                    if Globals.DEBUG['TCP']:
                        sys.stdout.write("CLIENT_INFO: Recieved {0} from {1}\n".format(data,self.address))
                    flag = b'fr\x00'
                    if data == flag:
                        csend = bytearray(self.jse.encode(Globals.dts)+'\x00',"UTF-8")
                        self.client.send(csend)
                else:
                    if Globals.INFO['TCP']:
                        sys.stdout.write("CLIENT_INFO: Closing client {0}\n".format(self.address))
                    break
                if self.closeEvent.isSet():
                    self.closeEvent.clear()
                    break
        except:
            e = sys.exc_info()
            sys.stderr.write('CLIENT_ERROR: {0}: {1}\n'.format(e[0],e[1]))
            traceback.print_tb(e[2])
            if Globals.INFO['TCP']:
                sys.stdout.write("CLIENT_INFO: Closing client {0}\n".format(self.address))
        finally:
            self.client.close()

    def close(self):
        self.closeEvent.set()

    def getCloseEvent(self):
        return self.closeEvent
