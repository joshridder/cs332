# A reliable file transfer server that works over UDP.
# Josh Ridder for CS332 @ Calvin Univeristy
# 10-31-21
# Usage: receiver.py -p [port] -o [output filename] -d [debug switch]

import argparse
import socket
import select
import sys
import random

PACKET_SIZE = 1450
HEADER_SIZE = 13

# parser for port and filename args
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", dest="port", help="port to listen on", default=2000)
parser.add_argument("-o", "--output", dest="output", help="filename of output file", default="output")
parser.add_argument("-d", "--debug", dest="debug", help="debug switch for extra output", default=False, type=bool)
args = parser.parse_args()

try:
    output_file = open(args.output, "wb")
except Exception as e:
    print("There was an error creating or opening the output file.\n", e)
    sys.exit(1)

try:
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(("0.0.0.0", int(args.port)))
except Exception as e:
    print("There was an error creating the socket.\n", e)
    sys.exit(1)

bytes_read = 0
session_id = -1
expected_packet_id = 0

print("Transferring...")

while True:

    read, write, error = select.select([receiver_socket], [], [])

    # recvfrom returns a tuple of (bytes, address)
    # - header is the first 12 bytes of payload
    data = receiver_socket.recvfrom(PACKET_SIZE + HEADER_SIZE)
    data_header = data[0][:12]
    data_ack_flag = data[0][12]
    data_payload = data[0][13:]
    data_address = data[1]

    connection_id = int.from_bytes(data_header[:4], "big")
    filesize = int.from_bytes(data_header[4:8], "big")
    packet_id = int.from_bytes(data_header[8:], "big")

    if args.debug:
        print("packet", packet_id, "arrived.\nack flag is", data_ack_flag)

    # ignore packets that don't share id
    if packet_id == 0:
        session_id = connection_id
    if connection_id != session_id:
        continue

    # send an ack packet if indicated as necessary by flag
    # ACK packet format: session_id (4 bytes) + packet_id (4 bytes)
    if data_ack_flag and packet_id <= expected_packet_id:
        ack_packet = (connection_id).to_bytes(4, "big") + (packet_id).to_bytes(4, "big")
        receiver_socket.sendto(ack_packet, data_address)

    # write new data from payload if it's the next in sqeuence, else restart loop
    if packet_id == expected_packet_id:
        output_file.write(data_payload)
        expected_packet_id += 1
        bytes_read += len(data_payload)
        if args.debug:
            print("packet", packet_id, "written to file")
    else:
        if args.debug:
            print("dropped")
        continue

    # halts receiving once program has received full file
    if bytes_read >= filesize:
        receiver_socket.close()
        break

output_file.close()
print("File transferred.")
