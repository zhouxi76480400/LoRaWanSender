from multiprocessing import Process, Queue
import os
import LoraSerial

# UDP傳入訊息的port
UDP_IN_PORT = 35000

# UDP傳出訊息的port
UDP_OUT_PORT = 35001

# 串列的port
LORA_SERIAL_PORT = 'com1'


# 首先我們需要兩個執行緒

# 和本地通訊用的process 需要指定入口port和出口port
def udp_process(message_queue: Queue, in_port, out_port):
    print("udp process is :{0}".format(os.getpid()))


# 啓動串列執行緒
def serial_process(message_queue: Queue, serial_port):
    print("lora process is :{0}".format(os.getpid()))
    LoraSerial.start_lora_forwarder(message_queue, serial_port)


if __name__ == '__main__':
    print("main process is :{0}".format(os.getpid()))
    q = Queue()
    process_udp = Process(target=udp_process, args=(q, UDP_IN_PORT, UDP_OUT_PORT,))
    process_lora = Process(target=serial_process, args=(q, LORA_SERIAL_PORT,))
    process_udp.start()
    process_lora.start()
    process_lora.join()
    process_udp.join()
    process_lora.terminate()
    process_udp.terminate()


