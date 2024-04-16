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
import dbquery
import argparse
import threading
import PyQt5.QtWidgets
import PyQt5.QtCore
import PyQt5.QtGui

#-----------------------------------------------------------------------

def get_arguments():
	if len(sys.argv) != 3:
		# print(': Usage: python %s port' % sys.argv[0], file=sys.stderr)
		print(sys.argv[0] + ': Usage: python %s host' % sys.argv[1] + ' %s port' % sys.argv[2], file=sys.stderr)
		sys.exit(1)

	# print('CPU count:', multiprocessing.cpu_count())

	parser = argparse.ArgumentParser(description = 'Client for regristrar application', allow_abbrev=False)
	parser.add_argument("host", type = str, help="the host on which the server is running")
	parser.add_argument("port", type = int, help="the port at which the server is listening")

	args = parser.parse_args()

	try:
		host = args.port
		port = int(args.delay)
	except Exception:
		print(sys.argv[0] + ': Port must be an integer', file=sys.stderr)
		sys.exit(2)

	return host, port

#-----------------------------------------------------------------------

def create_control_frame():
	## Label Widgets and align them
	dept_label = PyQt5.QtWidgets.QLabel('Dept: ')
	dept_label.setAlignment(PyQt5.QtCore.Qt.AlignRight | PyQt5.QtCore.Qt.AlignVCenter)

	crsnum_label = PyQt5.QtWidgets.QLabel('Number: ')
	crsnum_label.setAlignment(PyQt5.QtCore.Qt.AlignRight | PyQt5.QtCore.Qt.AlignVCenter)
	
	area_label = PyQt5.QtWidgets.QLabel('Area: ')
	area_label.setAlignment(PyQt5.QtCore.Qt.AlignRight | PyQt5.QtCore.Qt.AlignVCenter)
	
	title_label = PyQt5.QtWidgets.QLabel('Title: ')
	title_label.setAlignment(PyQt5.QtCore.Qt.AlignRight | PyQt5.QtCore.Qt.AlignVCenter)

	# LineEdit Widgets
	dept_lineedit = PyQt5.QtWidgets.QLineEdit()
	crsnum_lineedit = PyQt5.QtWidgets.QLineEdit()
	area_lineedit = PyQt5.QtWidgets.QLineEdit()
	title_lineedit = PyQt5.QtWidgets.QLineEdit()

	# control frame layout
	control_layout = PyQt5.QtWidgets.QGridLayout() # uses default spacing & content margins

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

	control_frame = PyQt5.QtWidgets.QFrame() # top section where we input queries
	control_frame.setLayout(control_layout)

	return control_frame, dept_lineedit, crsnum_lineedit, area_lineedit, title_lineedit

def create_output_frame():
	global classes

	# output frame layout
	output_layout = PyQt5.QtWidgets.QGridLayout()
	output_layout.setContentsMargins(0, 0, 0, 0)    # set contents margins (not default)
	output_layout.setSpacing(0)                     # set spacing (not default)
	output_layout.addWidget(classes, 0, 0)
	output_frame = PyQt5.QtWidgets.QFrame() # bottom section where the query output is diaplyed
	output_frame.setLayout(output_layout)

	return output_frame

def create_central_frame(control_frame, output_frame):
	# central frame layout
	control_frame, _, _, _, _ = create_control_frame()
	output_frame = create_output_frame()

	central_layout = PyQt5.QtWidgets.QGridLayout()
	central_layout.addWidget(control_frame, 0, 0)
	central_layout.addWidget(output_frame, 1, 0)
	central_frame = PyQt5.QtWidgets.QFrame() # control frame + output frame
	central_frame.setLayout(central_layout)

	return central_frame

def launch():
	global classes
	global host
	global port

	try:
		with socket.socket() as sock:
			sock.connect((host, port))
			query_type = "getOverviews"
			overviews_query = cmv.Query(query_type, None, None, None, None, None)
			flo = sock.makefile(mode = 'wb')
			pickle.dump(overviews_query, flo)
			flo.flush()

			flo = sock.makefile(mode = 'rb')
			overviews = pickle.load(flo)
			for row in overviews:
				classes.addItem(row)
			flo.flush()
	except EOFError:
		print(sys.argv[0] + ': End of File', file=sys.stderr)
		sys.exit(1)

# def submit_button_slot():
# 	global classes
# 	global host
# 	global port

# 	classes.clear()
# 	try:
# 		with socket.socket() as sock:
# 			sock.connect((host, port))
# 			query_type = "getOverviews"
# 			_, dept, crsnum, area, title = create_control_frame()
# 			overviews_query = cmv.Query(query_type, dept.text(), crsnum.text(), area.text(), title.text(), None)
# 			flo = sock.makefile(mode = 'wb')
# 			pickle.dump(overviews_query, flo)
# 			flo.flush()

# 			flo = sock.makefile(mode = 'rb')
# 			overviews = pickle.load(flo)
# 			for row in overviews:
# 				classes.addItem(row)
# 			flo.flush()
# 	except EOFError:
# 		print(sys.argv[0] + ': End of File', file=sys.stderr)
# 		sys.exit(1)

def class_details_slot():
	global classes
	global host
	global port

	classid = classes.currentItem().get_classid()

	try:
		with socket.socket() as sock:
			sock.connect((host, port))
			query_type = "getDetails"
			details_query = cmv.Query(query_type, None, None, None, None, classid)
			flo = sock.makefile(mode = 'wb')
			pickle.dump(details_query, flo)
			flo.flush()

			flo = sock.makefile(mode = 'rb')
			details = pickle.load(flo)
			PyQt5.QtWidgets.QMessageBox.information(window, 'Class Details', details)
			flo.flush()
		
	except Exception as ex:
		print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
		sys.exit(1)


def main():

	global host
	global port
	global window
	global classes

	host, port = get_arguments()
	
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	
	classes = PyQt5.QtWidgets.QListWidget()
	#  classes.setFont(PyQt5.QtGui.QFont('Courier New', 10))
	classes.doubleClicked.connect(class_details_slot)

	control_frame = create_control_frame()
	output_frame = create_output_frame()
	central_frame = create_central_frame(control_frame, output_frame)

	# Main Window (Class Search) details
	window = PyQt5.QtWidgets.QMainWindow()
	window.setWindowTitle('Princeton University Class Search')
	window.setCentralWidget(central_frame)
	screen_size = PyQt5.QtWidgets.QDesktopWidget().screenGeometry()
	window.resize(screen_size.width()//2, screen_size.height()//2)	
	window.show()

	launch()
	classes.setCurrentRow(0)
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
