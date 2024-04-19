#!/usr/bin/env python

#-----------------------------------------------------------------------
# reg.py
# Authors: Wangari Karani & Alfred Ripoll
#-----------------------------------------------------------------------

# import cmv
import sys
import queue 
import socket
import pickle
import argparse
import threading
from PyQt5 import QtGui, QtCore, QtWidgets

#-----------------------------------------------------------------------

def get_arguments():
	
	parser = argparse.ArgumentParser(description = 'Client for regristrar application', allow_abbrev=False)
	parser.add_argument("host", type = str, help="the host on which the server is running")
	parser.add_argument("port", type = int, help="the port at which the server is listening")

	args = parser.parse_args()

	try:
		host = args.host
		port = int(args.port)
	except Exception as ex:
		print(ex, file=sys.stderr)
		sys.exit(2)

	return host, port

#-----------------------------------------------------------------------

def create_control_frame():
	## Label Widgets and align them
	dept_label = QtWidgets.QLabel('Dept: ')
	dept_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

	crsnum_label = QtWidgets.QLabel('Number: ')
	crsnum_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
	
	area_label = QtWidgets.QLabel('Area: ')
	area_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
	
	title_label = QtWidgets.QLabel('Title: ')
	title_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

	# LineEdit Widgets
	dept_lineedit = QtWidgets.QLineEdit()
	crsnum_lineedit = QtWidgets.QLineEdit()
	area_lineedit = QtWidgets.QLineEdit()
	title_lineedit = QtWidgets.QLineEdit()

	# control frame layout
	control_layout = QtWidgets.QGridLayout() # uses default spacing & content margins

	control_layout.addWidget(dept_label, 0, 0)
	control_layout.addWidget(crsnum_label, 1, 0)
	control_layout.addWidget(area_label, 2, 0)
	control_layout.addWidget(title_label, 3, 0)

	control_layout.addWidget(dept_lineedit, 0, 1)
	control_layout.addWidget(crsnum_lineedit, 1, 1)
	control_layout.addWidget(area_lineedit, 2, 1)
	control_layout.addWidget(title_lineedit, 3, 1)

	control_layout.setColumnStretch(0, 0)
	control_layout.setColumnStretch(1, 1)
	control_layout.setColumnStretch(2, 0)
	control_layout.setSpacing(6)
	control_layout.setContentsMargins(0, 0, 0, 0)    # set contents margins (not default)

	control_frame = QtWidgets.QFrame() # top section where we input queries
	control_frame.setLayout(control_layout)

	return control_frame, dept_lineedit, crsnum_lineedit, area_lineedit, title_lineedit

#-----------------------------------------------------------------------

def create_output_frame(classes):
	# output frame layout
	output_layout = QtWidgets.QGridLayout()
	output_layout.setContentsMargins(0, 0, 0, 0)    # set contents margins (not default)
	output_layout.setSpacing(0)                     # set spacing (not default)
	output_layout.addWidget(classes, 0, 0)
	output_frame = QtWidgets.QFrame() # bottom section where the query output is diaplyed
	output_frame.setLayout(output_layout)

	return output_frame

#-----------------------------------------------------------------------

def create_central_frame(control_frame, output_frame):
	# central frame layout
	central_layout = QtWidgets.QGridLayout()
	central_layout.setContentsMargins(0, 0, 0, 0)    # set contents margins (not default)
	central_layout.setSpacing(0)    
	central_layout.setRowStretch(0, 0)
	central_layout.setRowStretch(1, 0)                 
	central_layout.addWidget(control_frame, 0, 0, 1, 3)
	central_layout.addWidget(output_frame, 1, 0)
	central_frame = QtWidgets.QFrame() # control frame + output frame
	central_frame.setLayout(central_layout)

	return central_frame

#-----------------------------------------------------------------------

def class_details_slot_helper(host, port, window, detail_overview):
	# get selected items, 
	# get text, strip spaces, split to convert it to words
	# get the first item which is classid, convert to int
	# courses = classes.selectedItems()
	# if len(courses) != 1:
	# 	print('Error: select one course')

	# course = courses[0]
	# # courseinfo = QtWidgets.QTextEdit().setText()
	# courseinfo = course.text()
	# courseinfo.strip()
	# courseinfo.split()
	classid = detail_overview[0]
 
	try:
		with socket.socket() as sock:
			sock.connect((host, port))
			details_query = ["get_detail", int(classid)]
			flo = sock.makefile(mode = 'wb')
			pickle.dump(details_query, flo)
			flo.flush()

			flo = sock.makefile(mode = 'rb')
			details = pickle.load(flo)			
			class_details = str(details[1])
			QtWidgets.QMessageBox.information(window, 'Class Details', class_details)
			flo.flush()
			return class_details
		
	except Exception as ex:
		print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
		sys.exit(1)

#-----------------------------------------------------------------------

class WorkerThread(threading.Thread):
	
	def __init__(self, host, port, dept, crsnum, area, title, event_queue):
		threading.Thread.__init__(self)
		self._host = host
		self._port = port		
		self._dept = dept
		self._coursenum = crsnum
		self._area = area
		self._title = title
		self._event_queue = event_queue
		self._should_stop = False
		
	def stop(self):
		self._should_stop = True
		
	def run(self):
		try:
			with socket.socket() as sock:
				sock.connect((self._host, self._port))
				portflow = sock.makefile(mode='wb')
				overviews_query = {'dept': self._dept, 'coursenum': self._coursenum, 'area': self._area, 'title': self._title}
				pickle.dump(['get_overviews', overviews_query], portflow)
				portflow.flush()

				flo = sock.makefile(mode='rb')
				overviews_output = pickle.load(flo)
			if not self._should_stop:
				self._event_queue.put((overviews_output))
		except Exception as ex:
			if not self._should_stop:
				self._event_queue.put((False, str(ex)))

#-----------------------------------------------------------------------

def poll_event_queue_helper(event_queue, classes):

	while True:
		try:
			item = event_queue.get(block=False)
		except queue.Empty:
			break
		classes.clear()
		successful, overviews = item		
		if successful:
			for course in overviews:
				row = '%5s %3s %4s %3s %-40s' % (course['classid'], course['dept'], course['coursenum'], course['area'], course['title'])
				classes.addItem(row)						
		else:
			print(sys.argv[0] + overviews, file=sys.stderr)
			sys.exit(1)

#-----------------------------------------------------------------------

def main():

	host, port = get_arguments()
	
	app = QtWidgets.QApplication(sys.argv)
	
	classes = QtWidgets.QListWidget()

	control_frame, dept_lineedit, crsnum_lineedit, area_lineedit, title_lineedit = create_control_frame()
	output_frame = create_output_frame(classes)
	output_frame.setFont(QtGui.QFont('Courier New', 10))
	central_frame = create_central_frame(control_frame, output_frame)

	# Main Window (Class Search) details
	window = QtWidgets.QMainWindow()
	window.setWindowTitle('Princeton University Class Search')
	window.setCentralWidget(central_frame)
	screen_size = QtWidgets.QDesktopWidget().screenGeometry()
	window.resize(screen_size.width()//2, screen_size.height()//2)	

	# Create an event queue and a timer that polls it
	event_queue = queue.Queue()

	def poll_event_queue():
		poll_event_queue_helper(event_queue, classes)
	event_queue_timer = QtCore.QTimer()
	event_queue_timer.timeout.connect(poll_event_queue)
	event_queue_timer.setInterval(100) # milliseconds
	event_queue_timer.start()

	# Handle signals
	worker_thread = None
	def submit_slot():
		nonlocal worker_thread
		dept = dept_lineedit.text()
		coursenum = crsnum_lineedit.text()
		area = area_lineedit.text()
		title = title_lineedit.text()
		if worker_thread is not None:
			worker_thread.stop()
		worker_thread = WorkerThread(host, port, dept, coursenum, area, title, event_queue)
		worker_thread.start()

	debounce_timer = None
	def debounced_submit_slot():
		nonlocal debounce_timer
		if debounce_timer is not None:
			debounce_timer.cancel()
		debounce_timer = threading.Timer(0.5, submit_slot)
		debounce_timer.start()

	# def details slot
	# define outside main a helper function and into that pass classes
	def class_details_slot():
		class_details_slot_helper(host, port, window, classes.currentItem().text().strip().split())

	dept_lineedit.textChanged.connect(debounced_submit_slot)
	crsnum_lineedit.textChanged.connect(debounced_submit_slot)
	area_lineedit.textChanged.connect(debounced_submit_slot)
	title_lineedit.textChanged.connect(debounced_submit_slot)
	classes.itemActivated.connect(class_details_slot)
	
	# Start up
	window.show()
	submit_slot()	
	classes.setCurrentRow(0)
	sys.exit(app.exec_())

#-----------------------------------------------------------------------
if __name__ == '__main__':()
main()
