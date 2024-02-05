#Importing essential modules
import numpy as np	
import pyaudio
import struct
import math
from PyQt5.Qt import *
from pyqtgraph import PlotWidget
from PyQt5 import QtCore
import pyqtgraph as pq
import pyaudio
import functools
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationTool
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
#Defining constants
CHUNK = 1024      
INITIAL_TAP_THRESHOLD = 0.010
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 1
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME					 
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

def get_rms( block ):
	# RMS amplitude is defined as the square root of the 
	# mean over time of the square of the amplitude.
	# so we need to convert this string of bytes into 
	# a string of 16-bit samples...

	# we will get one short out for each 
	# two chars in the string.
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )

	# iterate over the block.
	sum_squares = 0.0
	for sample in shorts:
		# sample is a signed short in +/- 32768. 
		# normalize it to 1.0
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n
		
	return math.sqrt( sum_squares / count )
class TapTester(object):
	def __init__(self):
		self.pa = pyaudio.PyAudio()
		self.stream = self.open_mic_stream()
		self.tap_threshold = INITIAL_TAP_THRESHOLD
		self.noisycount = MAX_TAP_BLOCKS+1 
		self.quietcount = 0 
		self.errorcount = 0
	def stop(self):
		self.stream.close()
	def find_input_device(self):
		device_index = None			   
		for i in range( self.pa.get_device_count() ):	  
			devinfo = self.pa.get_device_info_by_index(i)	
			#print( "Device %d: %s"%(i,devinfo["name"]) )

			for keyword in ["mic","input"]:
				if keyword in devinfo["name"].lower():
					print( "Found an input: device %d - %s"%		(i,devinfo["name"]) )
					device_index = i
					return device_index

		if device_index == None:
			print( "No preferred input found; using default input device." )

		return device_index
	def open_mic_stream( self ):
		device_index = self.find_input_device()

		stream = self.pa.open(	 format = FORMAT,
								channels = CHANNELS,
								rate = RATE,
								input = True,
								input_device_index = device_index,
								frames_per_buffer = CHUNK) #INPUT_FRAMES_PER_BLOCK)

		return stream
	def tapDetected(self):
		print ("Tap!")
	def listen(self):
		try:
			block = self.stream.read(CHUNK)
		except IOError as e:
			# dammit. 
			self.errorcount += 1
			#print( "(%d) Error recording: %s"%(self.errorcount,e) )
			self.noisycount = 1
			return

		RMS = get_rms( block )
		dataInt = struct.unpack(str(CHUNK) + 'h', block)
		#dataInt = np.median(dataInt)
		#print(dataInt)
		data1 = np.fromstring(self.stream.read(CHUNK),dtype=np.int16)		# read data and converting read Audio samples to 1D array (16 bit Integers)
		data1 = data1 * np.hanning(len(data1))		# hanning function provides good frequency resolution and leakage protection with fair amplitude accuracy
		fft = abs(np.fft.fft(data1).real)			# calculates the single-dimensional n-point DFT - - compute DFT with optimized FFT
		fft = fft[:int(len(fft)/2)]
		freq = np.fft.fftfreq(CHUNK,1.0/RATE)		#  frequencies associated with the coefficients.
		freq = freq[:int(len(freq)/2)]
		freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1


		#dataInt = functools.reduce(lambda sub, ele: sub * 10 + ele, dataInt)
		dataInt2=np.abs((dataInt))*2/(11000*CHUNK)
		#print("RMS!!",RMS)
		import numpy
		#current_dba = math.log(20, 10) * (RMS/ 20)
		current_dba = 20*numpy.log10(RMS)
		#print("DB!!",current_dba)
		if RMS > self.tap_threshold:
			# noisy block
			self.quietcount = 0
			self.noisycount += 1
			if self.noisycount > OVERSENSITIVE:
				# turn down the sensitivity
				self.tap_threshold *= 1.1
		else:			 
			# quiet block.
			#print("Quiet block!!")
			if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
				self.tapDetected()
			self.noisycount = 0
			self.quietcount += 1
			if self.quietcount > UNDERSENSITIVE:
				# turn up the sensitivity
				self.tap_threshold *= 0.9
		return RMS,dataInt,freqPeak,current_dba
#Class for 
class Window(QWidget):
    def __init__(self):
        self.tt=TapTester()
        super().__init__()
        self.setWindowTitle('PyAudio')
        self.resize(600,600)
        #Main Layout is Grid Layout. 
        self.hbox = QHBoxLayout(self)
        self.vbox_one=QVBoxLayout(self)
        self.vbox_two=QVBoxLayout(self)
        self.splitter_one=QSplitter(Qt.Horizontal)
        self.splitter_two=QSplitter(Qt.Vertical)       
        #Object Declaration for Menu Bar,Setting style.
        self.menubar = QMenuBar()
        self.hbox.setMenuBar(self.menubar)
        #Adding Actions to Menubar => Play action,Stop action, Pause action and Record action.
        self.update_menubar()
	    #Adding Snap action. Clicking this action will trigger the snap function. It is used to take screenshot of the GUI
        self.snap.triggered.connect(self.take_snap)
        #Declare rms,db,frequency variables
        self.declare_constants()
        #Setup canvas for Plots
        self.setup_canvas()
        #Declare data for plot
        self.declare_data()
        #Design graph, set limits etc
        self.design_graph()
        #plot and draw
        self.draw_graph()
        #declare text browser
        self.declare_text_browser()
        #append default data to text browsers
        self.add_default_data()
        #start timer
        self.timer = pq.QtCore.QTimer()
        #start play,pause,stop
        self.play.triggered.connect(self.start_app)
        self.pause.triggered.connect(self.pause_aud)
        self.stop.triggered.connect(self.stop_app)
        #log enable and disable
        self.start_log.triggered.connect(self.log_enable)	
        self.end_log.triggered.connect(self.log_disable)
        #add plots and text browsers to layout
        self.add_layers()
        #set the layout
        self.setLayout(self.hbox)	
        self.show()
    def log_enable(self):
        #print("Logging now!!!!")
        self.log_par=True
    def log_disable(self):
        self.log_par=False
    def stop_app(self):
        sys.exit(app.exec())
    def pause_aud(self):
        self.timer.stop()
    def start_app(self):

        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
	    
    def take_snap(self):
        #Used to take the snap of the GUI
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow( self.winId() )
        screenshot.save('shot.jpg', 'jpg')
    def update_menubar(self):
        self.menubar.setStyleSheet("background-color: gray;")
        self.actionFile1 = self.menubar.addMenu("Control")
        self.actionFile4 = self.menubar.addMenu("Record")
        self.snap=self.actionFile4.addAction("Snap")
        self.start_log=self.actionFile4.addAction("Start Log")
        self.end_log=self.actionFile4.addAction("End Log")
        self.play=self.actionFile1.addAction("Play")
        self.pause=self.actionFile1.addAction("Pause")
        self.stop=self.actionFile1.addAction("Stop")
    def declare_constants(self):
        self.peak=0
        self.rms=0
        self.db=0	
        self.iter=0
        self.file_one=open('myfile.txt', 'w')
        self.log_par=False
    def setup_canvas(self):
        self.figure_one = plt.figure()
        #self.figure_two = plt.figure()
        self.canvas_one = FigureCanvas(self.figure_one)
        #self.canvas_two = FigureCanvas(self.figure_two)
        self.figure_one.clear()
        #self.figure_two.clear()    
    def declare_data(self):
        self.x_data_one=np.linspace(0, RATE, CHUNK)	
        self.x_data_two=np.arange(0,2*CHUNK,2)
        self.y_data_one=np.random.rand(CHUNK)
        self.y_data_two=np.random.rand(CHUNK)
    def design_graph(self):
        self.ax_one=self.figure_one.add_subplot(111)
        self.ax_one.set_xlim(0,CHUNK)
        self.ax_one.set_ylim(-32000,32000)
        #self.ax_two=self.figure_two.add_subplot(111)
        # self.ax_two.set_xlim(20,RATE/2)
        # self.ax_two.set_ylim(0,1)
    def draw_graph(self):
        self.plot_one,=self.ax_one.plot(self.x_data_two,self.y_data_one)
        #self.plot_two,=self.ax_two.semilogx(self.x_data_two,self.y_data_two)
        self.canvas_one.draw()	
        #self.canvas_two.draw()
    def declare_text_browser(self):
        self.output_rd_3 = QTextBrowser()
        self.output_rd_4 = QTextBrowser()
        self.output_rd_5 = QTextBrowser()
    def add_default_data(self):
        self.output_rd_3.append("RMS Value \n")
        self.output_rd_4.append("Peak Frequency \n")
        self.output_rd_5.append("DB Value \n")
        self.output_rd_3.append(str(self.rms))
        self.output_rd_4.append(str(self.peak))
        self.output_rd_5.append(str(self.db))
    def add_layers(self):
        self.splitter_one.addWidget(self.output_rd_3)
        self.splitter_one.addWidget(self.output_rd_4)
        self.splitter_one.addWidget(self.output_rd_5)
        self.splitter_two.addWidget(self.splitter_one)
        self.splitter_two.addWidget(self.canvas_one)
        self.hbox.addWidget(self.splitter_two)
        #self.hbox.addLayout(self.vbox_one)
    def update_data(self):
        self.iter+=1 
        #print(self.iter)
        self.rms,x,self.peak,self.db=self.tt.listen()
        self.output_rd_3.clear()
        self.output_rd_3.append("RMS Value \n")
        self.output_rd_3.append((str(self.rms)))
        self.output_rd_4.clear()
        self.output_rd_4.append("Peak Frequency \n")
        self.output_rd_4.append((str(self.peak)))
        self.output_rd_5.clear()
        self.output_rd_5.append("DB \n")
        self.output_rd_5.append((str(self.db)))
        self.plot_one.set_ydata(x)
        #self.plot_two.set_ydata(np.abs(np.fft.fft(x))*2/(11000*CHUNK))
        self.canvas_one.draw()
        #self.canvas_two.draw()
        self.canvas_one.flush_events()
        #self.canvas_two.flush_events()
        if self.log_par==True:
            self.log_it()
    def log_it(self):       
        self.file_one.write("\n Iteration : "+ str(self.iter))
        self.file_one.write("\n")
        self.file_one.write("RMS Value : "+str(self.rms) ) 
        self.file_one.write("\n")
        self.file_one.write("Peak Frequency : "+ str(self.peak))
        self.file_one.write("\n")
        self.file_one.write("DB : "+ str(self.db))
        self.file_one.write("\n")
        #self.file_one.close()
	      	   
	     
	    


if __name__ == '__main__':
    import sys
    # PyQt5 Program fixed writing
    #tt=TapTester()
    app = QApplication(sys.argv)

    # Instantiate and display the window bound to the drawing control
    window = Window()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())
