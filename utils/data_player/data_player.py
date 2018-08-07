import sys
import os
import time
import numpy as np
import scipy.misc
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class DataPlayback(QMainWindow):

    def __init__(self, parent=None):
        super(DataPlayback, self).__init__(parent)
        self.image_label=QLabel()
        self.image_label.setText("Please load a file")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.filename_label=QLabel("None Loaded")
        self.pbutton=QPushButton("Play")
        self.loadbutton=QPushButton("Load")
        self.loadbutton.clicked.connect(self.load_file)
        layout=QGridLayout()
        layout.addWidget(self.filename_label, 0, 0, 1, 2)
        layout.addWidget(self.image_label, 1, 0, 1, 2)
        layout.addWidget(self.pbutton, 2, 0, 1, 1)
        layout.addWidget(self.loadbutton, 2, 1, 1, 1)
        centralWidget=QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.timer=QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.setInterval(20)

        self.isLoaded=False
        self.isPlaying=False
        self.filename=''
        self.frames=None
        self.frame_number=0
        self.nframes=0

        self.setWindowTitle("Data Playback")
        self.show()

    def load_file(self):
        self.pbutton.clicked.connect(self.play_func)
        self.filename=QFileDialog.getOpenFileName(self)[0]
        print(self.filename)
        raw_data=np.load(self.filename)['arr_0']
        self.nframes=raw_data.shape[0]
        self.frame_number=0
        self.filename_label.setText(self.filename)
        self.isLoaded=True
        big_frames=[scipy.misc.imresize(np.flipud(i), 3.0, interp='nearest') for i in raw_data]
        self.frames=[i.tobytes() for i in big_frames]
        self.imshape=big_frames[0].shape

        qimg=QImage(self.frames[self.frame_number], self.imshape[1], self.imshape[0], self.imshape[1]*3, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))

    def play_func(self):
        self.pbutton.clicked.connect(self.pause_func)
        self.pbutton.setText("Pause")
        self.timer.start()
        self.isPlaying=True

    def pause_func(self):
        self.pbutton.clicked.connect(self.play_func)
        self.pbutton.setText("Play")
        self.timer.stop()
        self.isPlaying=False

    def next_frame(self):
        self.frame_number=(self.frame_number+1)%self.nframes
    
        qimg=QImage(self.frames[self.frame_number], self.imshape[1], self.imshape[0], self.imshape[1]*3, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))


app=QApplication(sys.argv)
player=DataPlayback()
app.exec_()
