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
import dbquery
import argparse
import threading
# import multiprocessing

#-----------------------------------------------------------------------

def consume_cpu_time(delay):
	initial_thread_time = time.thread_time()
	while (time.thread_time() - initial_thread_time) < delay:
		pass

#-----------------------------------------------------------------------

def handle_client(sock, delay):
	# Make some changes to this 
	# query = Query(None, None, None, None, None, None)
	flo = sock.makefile(mode='rb')
	# flo.write(query)
	info = pickle.load(flo)

	try:
		portflow = sock.makefile(mode = 'wb')

		if info.get_query_type() == "getDetails":
			print('Received command: get_details')
			success, details = dbquery.a1regdetails(info.get_classid())
			if success:
				pickle.dump((True, details), portflow)
			else:
				print(str(details), file=sys.stderr)
				pickle.dump((False, details), portflow)
		else:
			print('Received command: get_overviews')

			# Simulate a compute bound thread
			consume_cpu_time(delay)

			success, overviews = dbquery.a1reg(info.get_dept(), info.get_number(), info.get_area(), info.get_title())
			if success:
				pickle.dump((True, overviews), portflow)
			else:
				print(str(overviews), file=sys.stderr)
				pickle.dump((False, overviews), portflow)

		portflow.flush()
		sock.close()
		print("Closed socket in child thread")
		print("Exiting child thread: ")

	except Exception as ex:
		print(ex, file = sys.stderr)
		portflow = sock.makefile(mode='wb')
		pickle.dump(ex, portflow)
		portflow.flush()
		sys.exit(1)

#-----------------------------------------------------------------------

class ClientHandlerThread (threading.Thread):

	def __init__(self, sock, delay):
		threading.Thread.__init__(self)
		self._sock = sock
		self._delay = delay

	def run(self):
		print('Spawned child thread')

		flo = self._sock.makefile(mode='rb')
		# flo.write(query)
		info = pickle.load(flo)

		with self._sock:
			try:
				portflow = self._sock.makefile(mode = 'wb')

				if info.get_query_type() == "getDetails":
					print('Received command: get_details')
					success, details = dbquery.a1regdetails(info.get_classid())
					if success:
						pickle.dump((True, details), portflow)
					else:
						print(str(details), file=sys.stderr)
						pickle.dump((False, details), portflow)
				else:
					print('Received command: get_overviews')

				# Simulate a compute bound thread
				consume_cpu_time(self._delay)

				success, overviews = dbquery.a1reg(info.get_dept(), info.get_number(), info.get_area(), info.get_title())
				if success:
					pickle.dump((True, overviews), portflow)
				else:
					print(str(overviews), file=sys.stderr)
					pickle.dump((False, overviews), portflow)

				portflow.flush()
				self._sock.close()
				print("Closed socket in child thread")
				print("Exiting child thread")

			except Exception as ex:
				print(ex, file = sys.stderr)
				portflow = self._sock.makefile(mode='wb')
				pickle.dump(ex, portflow)
				portflow.flush()
				sys.exit(1)

		print('Closed socket in child thread')
		print('Exiting child thread: ' + info)

#-----------------------------------------------------------------------

def main():
	if len(sys.argv) != 3:
		print(': Usage: python %s port' % sys.argv[0], file=sys.stderr)
		sys.exit(1)

	# print('CPU count:', multiprocessing.cpu_count())

	parser = argparse.ArgumentParser(description = 'Server for regristrar application', allow_abbrev=False)
	parser.add_argument('port', type=int, help='the port at which the server should listen')
	parser.add_argument('delay', type=int, help='the number of seconds that the server should delay before responding to each client request')

	args = parser.parse_args()

	try:
		port = int(args.port)
		delay = int(args.delay)
	except Exception:
		print(sys.argv[0] + ': Port/Delay must be an integer', file=sys.stderr)
		sys.exit(2)

	try:
		server_sock = socket.socket()
		
		print('Opened server socket') 
		server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)      
		server_sock.bind(('', port))
		print('Bound server socket to port')
		server_sock.listen()
		print('Listening')

		while True:			
			sock, _ = server_sock.accept()
			with sock:
				print('Accepted connection, opened socket')
				client_handler_thread = ClientHandlerThread(sock, delay)
				client_handler_thread.start()

				# process = multiprocessing.Process(target=handle_client, args=[sock, delay])
				# process.start()
	except Exception as ex:
		print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
		sys.exit(1)

#-----------------------------------------------------------------------
if __name__ == '__main__':
	main()
