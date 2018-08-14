import sys
import io
import socket
import struct
import time
import datetime
import picamera
import threading

from dataCollector import DataCollector
from car import car
from controller_object import ControllerObject
from socket_wrapper import *
from observer import *
from streamer import *


time_format='%Y-%m-%d_%H-%M-%S'

#set up sockets for commands in and stream out
commands_server=socket.socket()
stream_server=socket.socket()
commands_server.bind(('', 8005))
stream_server.bind(('', 8000))
commands_server.listen(0)
stream_server.listen(0)
(commands_in_sock, address)=commands_server.accept()
(stream_out_sock, address)=stream_server.accept()

#set up some global variables
stream=io.BytesIO()
commands_lock=threading.Lock()
car_commands=[0, 0]


class termCondition(Observer):
    def __init__(self):
        self.term=False
        self.observe("stop_stream", self.stop)

    def stop(self, flag):
        self.term=True

    def isSet(self):
        return self.term


def server_process(stop_ev, sock, stream):
    while not stop_ev.isSet():
        if stream.tell()!=0:
            commands_lock.acquire()
            THR, STR=car_commands
            commands_lock.release()
            Flag("new_data", {"image":stream, "THR":THR, "STR":STR})
            stream.seek(0)
            stream.truncate()
        time.sleep(.0001)


carlos=car() #initialize car object
tc=termCondition()

js_source=SocketReader(commands_in_sock) #joystick input from socket
server_thread=threading.Thread(target=server_process, args=[tc, stream_out_sock, stream])
controller=ControllerObject(js_source) #controller handler
controller.start_thread()
streamer=Streamer(stream_out_sock)
collector=DataCollector()


try:
    server_thread.start()
    time.sleep(2)
    while not tc.isSet():
        commands=controller.carpoll() #get commands from controller
        carlos.go(commands[1], commands[0]) #tell car to execute commands
        commands_lock.acquire()
        car_commands=commands #put commands in shared variable so they can be read by other thread
        commands_lock.release()
        time.sleep(.01)

    server_thread.join()

finally:
    stream_out_sock.close()
    stream_server.close()
    controller.stop_thread()
    commands_in_sock.close()
    commands_server.close()
    print("connection closed")
