import threading
import datetime
import concurrent.futures
import numpy as np
from observer import *

time_format='%Y-%m-%d_%H-%M-%S'

def save_data(images, commands, img_file, comm_file):
    #saving can take a long time, we don't want it causing a delay in the thread
    np.savez(img_file, images)
    np.savez(comm_file, commands)

class DataCollector(Observer):
    def __init__(self):
        self.observe("dc_start", self.start_collecting)
        self.observe("dc_stop", self.stop_collecting)
        self.observe("new_data", self.write)
        self.num_frames=200
        self.imgs=np.zeros(self.num_frames, 128, 96, 3)
        self.commands=np.zeros(self.num_frames, 2)
        self.idx=0
        self.executor=concurrent.futures.ThreadPoolExecutor(max_workers=5)
        self.collect=False

    def start_collecting(self, flag):
        self.collect=True
        
    def stop_collecting(self, flag):
        self.collect=False

    def write(self, flag):
        if self.collect==True: #THIS IS NOT THE RIGHT WAY TO DO THIS! We should have an unobserve function
            image=io.BytesIO(flag.image.getvalue())
            imsize=image.seek(0, io.SEEK_END)
            THR=flag.THR
            STR=flag.STR
            imdata=np.reshape(np.fromstring(image, dtype=np.uint8), (96, 128, 3), 'C')
            self.imgs[self.idx]=imdata
            self.commands[self.idx]=np.array([STR, THR])
            self.idx+=1
            if self.idx==self.num_frames:
                self.idx=0
                nowtime=datetime.datetime.now()
                command_filename='commands_{0}'.format(nowtime.strftime(time_format))
                image_filename='imgs_{0}'.format(nowtime.strftime(time_format))
                self.executor.submit(save_data, np.copy(self.imgs), np.copy(self.commands), image_filename, command_filename)
                self.imgs[:]=0
                self.commands[:]=0





