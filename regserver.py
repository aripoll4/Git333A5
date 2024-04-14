#!/usr/bin/env python

#-----------------------------------------------------------------------
# regserver.py
# Authors: Wangari Karani & Alfred Ripoll
#-----------------------------------------------------------------------

import os
import sys
import socket
import pickle
import argparse
from cmv import Query

#-----------------------------------------------------------------------

def handle_client(sock):
    # Make some changes to this 
    # query = Query(None, None, None, None, None, None)
    flo = sock.makefile(mode='rb')
    # flo.write(query)
    info = pickle.load(flo)

    try:
        portflow = sock.makefile(mode = 'wb')

        if info.get_query_type() == "getDetails":
            print('Received command: get_details')
            details = Query.a1regdetails(info.get_query_type(), info.get_classid())
            pickle.dump(details, portflow)

        else:
            print('Received command: get_overviews')
            overviews = Query.a1reg(info.get_query_type(), info.get_dept(), info.get_number(), info.get_area(), info.get_title())
            pickle.dump(overviews, portflow)
        portflow.flush()

    except Exception as ex:
        print(ex, file = sys.stderr)
        portflow = sock.makefile(mode='wb')
        pickle.dump(ex, portflow)
        portflow.flush()

    flo.flush()    

#-----------------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print(sys.argv[0] + ': Usage: python %s port' % sys.argv[1], file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description = 'Server for regristrar application', allow_abbrev=False)
    parser.add_argument('port', type=int, help='the port at which the server should listen')
    
    args = parser.parse_args()

    try:
        port = args.port
        server_sock = socket.socket()
        print('Opened server socket')
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')

        while True:
            try: 
                sock, _ = server_sock.accept()
                with sock:
                    print('Accepted connection, opened socket')
                    handle_client(sock)
                    print('Closed socket')
            except Exception as ex:
                print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
                sys.exit(1)
    except Exception as ex:
                print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)
                sys.exit(1) 

#-----------------------------------------------------------------------
if __name__ == '__main__':
	main()
