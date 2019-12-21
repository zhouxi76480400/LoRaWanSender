from socketserver import BaseRequestHandler, UDPServer
from multiprocessing import Queue
import Sender
import os
import socket
import LoRaTextObject


class RequestHandler(BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        sock: socket.socket = self.request[1]
        client_address = self.client_address[0]
        # client_port = self.client_address[1]  # useless
        # 要把這個放到隊列中
        text_obj: LoRaTextObject.LoRaTextObject = LoRaTextObject.get_a_lora_txt_object(data)
        # 進入隊列
        Sender.request_send_queue.put(text_obj, block=True, timeout=None)

        # sock.sendto(b'a', (client_address, Sender.UDP_OUT_PORT))
        # print("pid:{0}".format(os.getpid())+",queue:{0}".format(Sender.request_send_queue))
        # print("?????->{0}".format(Sender.request_send_queue))


def start_udp_forwarder():
    server = UDPServer(('127.0.0.1', Sender.UDP_IN_PORT), RequestHandler)
    server.serve_forever()








