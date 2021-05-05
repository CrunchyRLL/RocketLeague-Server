import socket
import time
from threading import *

from Logic.Device import Device
from Logic.Player import Player
from Protocol.LogicMessageFactory import packets


def _(*args):
	print('[INFO]', end=' ')
	for arg in args:
		print(arg, end=' ')
	print()


print(r"""
__________               __           __  .____                                        
\______   \ ____   ____ |  | __ _____/  |_|    |    ____ _____     ____  __ __   ____  
 |       _//  _ \_/ ___\|  |/ // __ \   __\    |  _/ __ \\__  \   / ___\|  |  \_/ __ \ 
 |    |   (  <_> )  \___|    <\  ___/|  | |    |__\  ___/ / __ \_/ /_/  >  |  /\  ___/ 
 |____|_  /\____/ \___  >__|_ \\___  >__| |_______ \___  >____  /\___  /|____/  \___  >
        \/            \/     \/    \/             \/   \/     \//_____/             \/
                                                                                  v1.96 Season 3                                                               
""")


class Server:
	def __init__(self, ip: str, port: int):
		self.server = socket.socket()
		self.port = port
		self.ip = ip

	def start(self):
		self.server.bind((self.ip, self.port))
		_(f'Server started! Ip: {self.ip}, Port: {self.port}')
		while True:
			self.server.listen()
			client, address = self.server.accept()
			_(f'New connection! Ip: {address[0]}')
			ClientThread(client, address).start()


class ClientThread(Thread):
	def __init__(self, client, address):
		super().__init__()
		self.client = client
		self.address = address
		self.device = Device(self.client)
		self.player = Player(self.device)

	def recvall(self, length: int):
		data = b''
		while len(data) < length:
			s = self.client.recv(length)
			if not s:
				print("ERROR while receiving data!")
				break
			data += s
		return data

	def run(self):
		last_packet = time.time()
		while True:
			header = self.client.recv(7)
			if len(header) > 0:
				last_packet = time.time()
				packet_id = int.from_bytes(header[:2], 'big')
				length = int.from_bytes(header[2:5], 'big')
				data = self.recvall(length)

				if packet_id in packets:
					_(f'Received packet! Id: {packet_id}')
					message = packets[packet_id](self.client, self.player, data)
					message.decode()
					message.process()
				else:
					_(f'Packet not handled! ({packet_id})')
			if time.time() - last_packet > 10:
				_("Client disconnected!")
				self.client.close()
				break


if __name__ == '__main__':
	server = Server('0.0.0.0', 7777)
	server.start()
