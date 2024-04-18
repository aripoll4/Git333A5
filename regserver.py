#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserver.py
# Authors: Wangari Karani & Alfred Ripoll
#-----------------------------------------------------------------------

# import os
import sys
import time
import socket
import pickle
from dbquery import DBQuery
import argparse
import threading
# import multiprocessing

#-----------------------------------------------------------------------

def consume_cpu_time(delay):
	initial_thread_time = time.thread_time()
	while (time.thread_time() - initial_thread_time) < delay:
		pass

#-----------------------------------------------------------------------

class ClientHandlerThread (threading.Thread):

	def __init__(self, sock, delay):
		threading.Thread.__init__(self)
		self._sock = sock
		self._delay = delay

	def run(self):
		print('Spawned child thread')
		with self._sock:
			try:
				flo = self._sock.makefile(mode='rb')				
				queryinfo = pickle.load(flo)
				portflow = self._sock.makefile(mode = 'wb')

				if queryinfo[0] == "get_detail":
					print('Received command: get_detail')
					consume_cpu_time(self._delay)
					success, details = DBQuery.a1regdetails(queryinfo[1])
					details_output = [success, details]
					pickle.dump(details_output, portflow)
					
				else:
					print('Received command: get_overviews')
					consume_cpu_time(self._delay)
					querydict = queryinfo[1]
					success, overviews = DBQuery.a1reg(querydict['dept'], querydict['coursenum'], querydict['area'], querydict['title'])
					pickle.dump([success, overviews], portflow)

				portflow.flush()
				self._sock.close()
				print("Closed socket in child thread")
				print("Exiting child thread")

			except Exception as ex:
				print(ex, file = sys.stderr)				

		print('Closed socket in child thread')
		print('Exiting child thread')

#-----------------------------------------------------------------------

def main():
	if len(sys.argv) != 3:
		print(': Usage: python %s port' % sys.argv[0], file=sys.stderr)
		sys.exit(1)
		
	parser = argparse.ArgumentParser(description = 'Server for regristrar application', allow_abbrev=False)
	parser.add_argument('port', type=int, help='the port at which the server should listen')
	parser.add_argument('delay', type=int, help='the number of seconds that the server should delay before responding to each client request')

	args = parser.parse_args()

	try:
		port = int(args.port)
		delay = int(args.delay)
		server_sock = socket.socket()

		server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      
		print('Opened server socket') 
		server_sock.bind(('', port))
		print('Bound server socket to port')
		server_sock.listen()
		print('Listening')

		while True:			
			sock, _ = server_sock.accept()
			print('Accepted connection, opened socket')
			client_handler_thread = ClientHandlerThread(sock, delay)
			client_handler_thread.start()
	except Exception as ex:
		print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
		sys.exit(1)

#-----------------------------------------------------------------------
if __name__ == '__main__':
	main()
