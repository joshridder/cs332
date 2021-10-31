# 
# 
# 
# 
# 

import argparse
import socket
import sys
import tqdm
import os
import random

def find_location_in_file(filename, packet_no):
    filename.seek(packet_no * PACKET_SIZE, 0)
    return filename.read(PACKET_SIZE)

SEPARATOR = "<SEPARATOR>"
PACKET_SIZE = 1450
HEADER_SIZE = 13

#parser for port and filename args
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", dest="server", help="IP address / hostname of the server",
                    default="localhost")
parser.add_argument("-p", "--port", dest="port", help="port to listen on",
                    default="10000", type=int)
parser.add_argument("-i", "--input", dest="input", help="filename of input file",
                    default="input")
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
filesize = os.path.getsize(args.input)
header_ack_flag = (0).to_bytes(1, "big")
header_id_and_size = random.randint(0, 2 ** 32).to_bytes(4, "big") + filesize.to_bytes(4, "big")
header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag

# progress bar initialization
progress = tqdm.tqdm(range(filesize), f"Sending {args.input}", unit="B", unit_scale=True, unit_divisor=PACKET_SIZE)

# adapted from https://www.thepythoncode.com/code/send-receive-files-using-sockets-python
with open(args.input, "rb") as input_file:
    while True:
        bytes_to_send = find_location_in_file(input_file, packet_id)

        # send data if there is any left
        if not bytes_to_send:
            input_file.close()
            break

        # determine if ACK flag is necessary
        if since_last_ack == ack_gap:
            ack_gap += 1
            since_last_ack = 0
            header_ack_flag = (1).to_bytes(1, "big")
            header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
        # set header_ack_flag to 1 for flast packet
        elif PACKET_SIZE * packet_id >= filesize - PACKET_SIZE:
            header_ack_flag = (1).to_bytes(1, "big")
            header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
        else:
            since_last_ack += 1

        sender_socket.sendto(header + bytes_to_send, destination)

        # wait for ACK if packet was flagged as needing ACK
        if int.from_bytes(header_ack_flag, "big"):
            response_packet_data = sender_socket.recvfrom(PACKET_SIZE)[0]
            header_ack_flag = (0).to_bytes(1, "big")

        # update state variables
        packet_id += 1
        header = header_id_and_size + (packet_id).to_bytes(4, "big") + header_ack_flag
        progress.update(len(bytes_to_send))

sender_socket.close()