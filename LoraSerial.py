import serial_asyncio
import asyncio

from multiprocessing import Queue


def init_lora(serial_port):
    print(serial_port)


def start_lora_forwarder(message_queue: Queue, serial_port):
    init_lora(serial_port)

