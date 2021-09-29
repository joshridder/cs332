# Josh Ridder for CS332 at Calvin University
# 9-28-21
# 
# references:
# https://docs.python.org/3/howto/sockets.html
# https://pymotw.com/3/select/

import socket
import select
import argparse
import socket

parser = argparse.ArgumentParser(description="A prattle server")

parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="TCP port the server is listening on (default 12345)")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

# initialize server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", args.port))
server.listen()

# list to hold sockets with active connections
socks = [server]
if args.verbose:
    print(f'Started server on {args.port}')

while True:

    read_s, write_s, error_s = select.select(socks, socks, [])

    for sock in read_s:
        # accept new connection if client not already in socks
        if sock == server:
            client_socket, client_address = server.accept()
            client_socket.send(bytes("Thank you for connecting!", 'utf-8'))
            socks.append(client_socket)

            if args.verbose:
                print(f"Got connection from {client_address}")

        # accept message from client
        else:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if message == "":
                    raise socket.Error()
                if args.verbose:
                    print(f"Message received: \"{message}\"")
            except:
                # server either received empty messages, meaning client disconnected,
                # or message couldn't be read.
                if args.verbose:
                    print("Client removed from socket list.")
                socks.remove(sock)
                continue

            # send message to every other client connected to server upon recieving
            for other_client in socks:
                if other_client != sock and other_client != server:
                    try:
                        other_client.send(bytes(message, 'utf-8'))
                        if args.verbose:
                            print(f"Message sent: \"{message}\"")
                    except Exception as e:
                        print(f"There was a problem sending the message: {message}", e)