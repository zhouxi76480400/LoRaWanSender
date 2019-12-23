from multiprocessing import Process, Queue
import os
import LoraSerial
import UDPForwarder

# UDP傳入訊息的port
UDP_IN_PORT = 35000

# 串列的port
LORA_SERIAL_PORT = '/dev/tty.usbserial-1410'

LORA_SERIAL_BAUDRATE = 115200

# 一個lora包最大的hex字數
LORA_PACKET_MAX_BYTE_LENGTH = 96


# 首先我們需要兩個執行緒

# 和本地通訊用的process 需要指定入口port和出口port
def udp_process():
    print("udp process is :{0}".format(os.getpid()))
    UDPForwarder.start_udp_forwarder()


# 啓動串列執行緒
def serial_process():
    print("lora process is :{0}".format(os.getpid()))
    LoraSerial.start_lora_forwarder()


# 請求通過lora發送的隊列
request_send_queue = Queue()


# 是否發送成功的隊列
response_back_queue = Queue()


if __name__ == '__main__':
    print("main process is :{0}".format(os.getpid()))
    process_udp = Process(target=udp_process, args=())
    process_lora = Process(target=serial_process, args=())
    process_udp.start()
    process_lora.start()
    process_lora.join()
    process_udp.join()
    process_lora.terminate()
    process_udp.terminate()


