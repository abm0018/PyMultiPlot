import sys
import numpy as np
from pdb import set_trace
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from jet import colorMap

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.axs = plt.subplots(3, 1)
        self.fig.suptitle('')
        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        #sc.axes.plot(np.arange(0,1,1/10), np.arange(0,1,1/10)*5.2)
        self.filename = 'C:/file/name/here'
        self.curr_fft = 0
        self.FS = 100e3
        self.peak_freq = 0
        self.numpeaks = 3
        self.peaks = []
        toolbar = NavigationToolbar(self.sc, self)

        self.hscroll = QtWidgets.QScrollBar()
        self.hscroll.setOrientation(QtCore.Qt.Horizontal)
        self.hscroll.setRange(0,200)
        self.hscroll.valueChanged.connect(lambda: self.updatePlotH())

        self.vscroll = QtWidgets.QScrollBar()
        self.vscroll.setOrientation(QtCore.Qt.Vertical)
        self.vscroll.setRange(-100,100)
        self.vscroll.valueChanged.connect(lambda: self.updatePlotV())

        self.lineedit_filename = QtWidgets.QLineEdit()
        self.browsebutton = QtWidgets.QPushButton("Browse")
        self.browsebutton.clicked.connect(self.getData)

        layout_form = QtWidgets.QGridLayout() #QFormLayout()
        self.lineedit_FS = QtWidgets.QLineEdit("100e3")
        self.curr_fft_lab = QtWidgets.QLabel('')
        self.peak_freq_lab = QtWidgets.QLabel('')
        #layout_form.addRow("Sample Rate: ", self.lineedit_FS)
        layout_form.addWidget(QtWidgets.QLabel("Sample Rate: "), 0, 0)
        # layout_form.addWidget(QtWidgets.QLabel("Current FFT: "), 1, 0)
        # layout_form.addWidget(QtWidgets.QLabel("Peak Freq: "), 2, 0)
        layout_form.addWidget(self.lineedit_FS, 0, 1)
        # layout_form.addWidget(self.curr_fft_lab, 1, 1)
        # layout_form.addWidget(self.peak_freq_lab, 2, 1)

        layout_brows = QtWidgets.QHBoxLayout()
        layout_brows.addWidget(self.lineedit_filename)
        layout_brows.addWidget(self.browsebutton)

        layout_right = QtWidgets.QVBoxLayout()
        layout_right.addLayout(layout_brows)        
        layout_right.addWidget(toolbar)
        layout_right.addWidget(self.sc)
        layout_right.addLayout(layout_form)
        layout_right.addWidget(self.hscroll)
        

        layout_left = QtWidgets.QVBoxLayout()
        layout_left.addWidget(self.vscroll)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_left)
        layout.addLayout(layout_right)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def getData(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(self, "Data File", "C:/", "CSV Files (*.csv)")[0]
        f = open(self.filename, 'r')
        data = f.read().split(',')
        data = [float(point) for point in data if point]
        data = np.array(data)
        self.data = data

        self.lineedit_filename.setText(self.filename)
        self.sc.fig.suptitle(self.filename)
        self.FS = float(self.lineedit_FS.text())

        self.fft_len = 512
        tstop = len(data) * (1/self.FS)
        self.t = np.arange(0,tstop,1/self.FS)    
        
        self.updateFFT()
        self.updateRanges()
        self.plotData()

    def updateFFT(self):
        self.num_ffts = len(self.t) // self.fft_len
        self.Y = np.empty( shape=(self.num_ffts, self.fft_len) )
        self.img = np.ones( shape=(self.num_ffts, self.fft_len//2, 3), dtype=np.uint8 ) * 255
        self.FS = float(self.lineedit_FS.text())

        for i in range(0, self.num_ffts):
            self.Y[i] = abs(np.fft.fftshift( np.fft.fft( self.data[self.fft_len * i:(i+1)*self.fft_len] )))
            self.Y[i] /= max(self.Y[i])
            tmp = self.Y[i][self.fft_len//2:] # (2 * self.fft_len//2)]
            tmp = tmp[:self.fft_len//2]
            self.img[i] = colorMap(tmp)

        self.N = len(self.Y[0])//2
        self.fft_freqs = (self.FS/2) * np.arange(0,1,1/self.N)
        self.fft_freqs = self.fft_freqs[:len(self.Y[0])//2]                           
        self.freq_stop = self.fft_freqs[-1]

        self.xstart = (self.curr_fft) * self.fft_len
        self.xstop = min((1+self.curr_fft) * self.fft_len, len(self.data)) #min prevents us from trying to plot more data than exists
    
    def updateRanges(self):
        self.fft_start = 0
        self.updateVRange()
        self.updateHRange()        
        #self.hscroll.setPageStep(2) #did not seem to work, steps were still 1

    def updateVRange(self):
        self.vscroll.setRange(0, self.num_ffts-1)

    def updateHRange(self):
        self.hscroll.setRange(min(32, len(self.data)//2), len(self.data)//2)

    def plotData(self):
        FS = self.FS
        t = np.arange(self.curr_fft * (self.fft_len/FS), ((1+self.curr_fft) * (self.fft_len/FS)), 1/FS)
        t = t[:self.fft_len]

        peak_idx = self.Y[self.curr_fft][self.fft_len//2:].argmax()
        self.peak_freq = int(self.fft_freqs[peak_idx])

        self.sc.axs[0].cla()
        self.sc.axs[1].cla()
        self.sc.axs[2].cla()
        self.sc.axs[0].imshow(self.img, extent=[0, self.freq_stop, self.num_ffts, 0], aspect='auto') #waterfall plot
        self.sc.axs[0].set_title('')
        self.sc.axs[0].axhline(y=self.curr_fft, linewidth=2, color='white')
        self.sc.axs[1].plot(self.fft_freqs, 20 * np.log10(self.Y[self.curr_fft][self.fft_len//2:]))
        self.sc.axs[1].grid()
        self.sc.axs[1].set_title(f'{self.peak_freq}')
        self.sc.axs[2].plot(t, self.data[self.xstart:self.xstop])
        self.sc.axs[2].grid()
        self.sc.axs[2].set_title('')
        self.sc.draw()

    def updatePlotH(self): #if fft length changes, we need to change num ffts available and h cursor
        self.curr_fft = 0
        self.fft_len = 2 * self.hscroll.value()
        self.updateFFT()
        self.updateVRange()
        self.plotData()

    def updatePlotV(self):
        self.curr_fft = self.vscroll.value()
        self.xstart = (self.curr_fft) * self.fft_len
        self.xstop = min((1+self.curr_fft) * self.fft_len, len(self.data)) 
        self.plotData()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()

if __name__ == '__main__':
    main()