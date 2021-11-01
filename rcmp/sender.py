# A reliable file transfer client that works over UDP.
# Josh Ridder for CS332 @ Calvin Univeristy
# 10-31-21
# Usage: sender.py -s [server IP / hostname] -p [port] -i [input filename] -d [debug switch]

from timeout import *
import argparse
import socket
import sys
import os
import random

def find_location_in_file(filename, packet_no):
    filename.seek(packet_no * PACKET_SIZE, 0)
    return filename.read(PACKET_SIZE)

@timeout(2)
def receive_ack(socket, numBytes):
    return socket.recvfrom(numBytes)

SEPARATOR = "<SEPARATOR>"
PACKET_SIZE = 1450
HEADER_SIZE = 13
ACK_ON = 1
ACK_OFF = 0

#parser for port and filename args
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", dest="server", help="IP address / hostname of the server",
                    default="localhost")
parser.add_argument("-p", "--port", dest="port", help="port to listen on",
                    default="10000", type=int)
parser.add_argument("-i", "--input", dest="input", help="filename of input file",
                    default="input")
parser.add_argument("-d", "--debug", dest="debug", help="debug switch for extra output",
                    default=False, type=bool)
args = parser.parse_args()

# create socket to send data
try:
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    destination = (args.server, args.port)
except Exception as e:
    print("There was an error creating the socket.\n", e)
    sys.exit(1)

# make header for data
packet_id = 0
ack_gap = 0
since_last_ack = 0
last_acked_id = 0
final_ack_timeouts = 0
sending_first_packet = True
filesize = os.path.getsize(args.input)
header_ack_flag = (ACK_OFF).to_bytes(1, "big")
header_id_and_size = random.randint(0, 2 ** 32).to_bytes(4, "big") + filesize.to_bytes(4, "big")
header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag

print("Transferring...")

# adapted from https://www.thepythoncode.com/code/send-receive-files-using-sockets-python
with open(args.input, "rb") as input_file:
    while True:
        bytes_to_send = find_location_in_file(input_file, packet_id)

        # send data if any not acked
        if not bytes_to_send:
            input_file.close()
            break

        # determine if ACK flag is necessary           
        if since_last_ack == ack_gap and not sending_first_packet:
            ack_gap += 1
            since_last_ack = 0
            header_ack_flag = (ACK_ON).to_bytes(1, "big")
            header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
        # set header_ack_flag to ON for first and last packet
        elif PACKET_SIZE * packet_id >= filesize - PACKET_SIZE or sending_first_packet:
            sending_first_packet = False
            header_ack_flag = (ACK_ON).to_bytes(1, "big")
            header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
        else:
            # no ack required
            since_last_ack += 1

        # send packet to receiver
        sender_socket.sendto(header + bytes_to_send, destination)

        # wait for ACK if packet was flagged as needing ACK
        if int.from_bytes(header_ack_flag, "big"):
            try:
                response_packet_data = receive_ack(sender_socket, PACKET_SIZE)[0]
                last_acked_id = packet_id
                if args.debug:
                    print("last acked", packet_id)
                header_ack_flag = (ACK_OFF).to_bytes(1, "big")
            except TimeoutError:
                # not last packet
                if PACKET_SIZE * packet_id <= filesize - PACKET_SIZE:
                    if args.debug:
                        print("PACK MISSED")
                    # if ack timed out, set packet_id to last confirmed packet.
                    # loop will restart starting from the first packed not confirmed by most recent ack.
                    packet_id = last_acked_id
                    ack_gap = 0
                    since_last_ack = 0
                    sending_first_packet = True
                    # header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
                    # continue
                # last packet
                else:
                    if args.debug:
                        print("Final pack missed once...")
                    final_ack_timeouts += 1
                    # if packet isn't acked 5 times in a row, display message
                    while final_ack_timeouts < 5:
                        sender_socket.sendto(header + bytes_to_send, destination)
                        try:
                            response_packet_data = receive_ack(sender_socket, PACKET_SIZE)
                            break
                        except TimeoutError:
                            final_ack_timeouts += 1
                            if args.debug:
                                print("final pack missed again...")
                    else:
                        print("File transfer status unknown.")
                        break

        # update state variables
        packet_id += 1
        header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag

print("File transferred successfully!")
sender_socket.close()
