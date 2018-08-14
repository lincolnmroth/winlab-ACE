import sys
from observer import *
import time
import serial
import serial.tools.list_ports
import struct
import threading
import socket

class car(Observer):
    def __init__(self):
        self.speed = 0
        self.dir = 0
        self.port = None
        for p in serial.tools.list_ports.comports():
            print(p.description)
            if 'ttyACM' in p.description:
                print('Found arduino')
                self.port = serial.Serial(p.device, baudrate=576000)

        if self.port == None:
            print('Could not connect to Arduino')
            sys.exit(1)


        self.sending_lock = threading.Lock()
        out_stream = threading.Thread(target=self.keep_sending)
        out_stream.start()


    def go(self, STR, THR):
        self.speed = THR
        self.dir = STR

    def keep_sending(self):

        while True:
            self.sending_lock.acquire()
            self.send(self.speed, self.dir)
            self.sending_lock.release()
            time.sleep(0.05)

    def send(self, speed, dir):
        port = self.port
        out = 'Speed:' + str(self.speed) + ' Dir:' + str(self.dir)
        print(out)
        try:
            port.write((str(self.speed) + ':' + str(self.dir) + '\n').encode())
        except:
            pass

    def calib_start(self, flag):
        pass

    def calib_stop(self, flag):
        pass

    def cali_left(self, flag):
        pass

    def cali_right(self, flag):
        pass
