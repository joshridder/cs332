# Josh Ridder for CS332 at Calvin University
# 9-20-21
# 
# https://pymotw.com/3/select/ used as reference
#

import select
from socket import *
import sys
import argparse


parser = argparse.ArgumentParser(description="A prattle client")

parser.add_argument("-n", "--name", dest="name", help="name to be prepended in messages (default: machine name)")
parser.add_argument("-s", "--server", dest="server", default="127.0.0.1",
                    help="server hostname or IP address (default: 127.0.0.1)")
parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

# initialize socket with given info
s = socket()
try:
    s.connect((args.server, args.port))
except Exception as e:
    print("There was an error when creating the socket.\n", e)
    sys.exit(1)
if args.verbose:
    print("    Connection established with", args.server, "on port", args.port)

inputs = [s, sys.stdin]

while True:

    try:
        # select input that has data ready to be handled (either server socket or user input)
        read_s, write_s, error_s = select.select(inputs, [], [])

        for input in read_s:
            # socket has a message to be displayed from the server
            if input == s:
                line = s.recv(args.port).decode("utf-8").strip("\n")
                if args.verbose:
                    print("    Message recieved from", args.server, "on port", args.port)
                print(line)
                
            # stdin has a message to be sent - print and send over socket
            else:
                # format with <name> says: 
                line = "<" + args.name + "> says: " + str(sys.stdin.readline())
                try:
                    s.send(bytes(line, 'utf-8'))
                    if args.verbose:
                        print("    Message sent.")

                except Exception as e:
                    print("The message could not be sent.")
                    print(e)
                    sys.exit(1)

                sys.stdout.write(line)
                sys.stdout.flush()

    except Exception as e:
        print("There was a problem when attempting to select next input.\n", e)
        sys.exit(1)
