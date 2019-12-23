import serial
import Sender
import time
import LoRaTextObject
import socket

LORA_RESET_TIME_OUT = 60  # s


def send_successful_message(text_object: LoRaTextObject):
    print("{0}: send successful msg to port {1}".format(__name__, text_object.client_address[1]))
    send_msg_use_udp(text_object.client_address, b'{\"result\":0}')


def send_failed_message(text_object: LoRaTextObject):
    print("{0}: send failed msg to port {0}".format(__name__, text_object.client_address[1]))
    send_msg_use_udp(text_object.client_address, b'{\"result\":-1}')


def send_msg_use_udp(client_address, msg: bytes):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, client_address)


def block(_t):
    start_time = time.time() * 1000
    is_run = True
    if is_run:
        stop_time = time.time() * 1000
        if stop_time - start_time >= _t:
            is_run = False


class LoraHandleClass:
    # 實例
    ser: serial.Serial

    # 現在準備發送的object
    now_sending_text_obj: LoRaTextObject.LoRaTextObject

    # 現在這個包已經發送的offset值
    now_sending_text_start_position_offset = 0

    now_text_sending_failed = False

    def __init__(self):
        self.now_sending_text_obj = None

    def lora_init(self):
        print("{0}: init lora controller from {1}".format(__name__, Sender.LORA_SERIAL_PORT))
        self.ser = serial.Serial()
        self.ser.port = Sender.LORA_SERIAL_PORT
        self.ser.baudrate = Sender.LORA_SERIAL_BAUDRATE
        self.ser.timeout = 10
        self.ser.open()
        if self.ser.is_open:
            print("{0}: lora controller port open successful".format(__name__))
            # 給30秒鍾重置裝置
            now_time = time.time()
            is_waiting = True
            # 記錄是否重置成功
            is_reset_successful = False
            self.ser.write(b'at+set_config=device:restart\r\n')
            while is_waiting:
                if time.time() - now_time >= LORA_RESET_TIME_OUT:
                    is_waiting = False
                else:
                    now_uart_bytes_line = self.ser.readline()
                    # 如果成功重置裝置則跳出循環
                    if now_uart_bytes_line == b'[LoRa]:Join Success\r\n':
                        is_reset_successful = True
                        is_waiting = False
                    print("{0}: UART-->{1}".format(__name__, now_uart_bytes_line))
            # self.ser.close()
            if not is_reset_successful:
                if self.ser.is_open:
                    self.ser.close()
                self.lora_init()
            print("{0}: reset lora successful".format(__name__))

    def start_lora(self):
        while True:
            # 先判斷是否有剩下沒發送的
            if self.now_sending_text_obj is None:
                # 沒有剩下的 需要從隊列中拉一個來
                if not Sender.request_send_queue.empty():
                    print("拉隊列")
                    self.now_sending_text_obj = Sender.request_send_queue.get(block=True, timeout=None)
            else:
                # 這邊要執行發送任務
                if self.now_text_sending_failed:
                    # 不用繼續發送了 已經失敗 報告失敗
                    # 發送失敗消息
                    send_failed_message(self.now_sending_text_obj)
                    # print("{0}: Msg send failed".format(__name__))
                    self.now_sending_text_obj = None
                    print(self.now_sending_text_obj)
                    self.now_sending_text_start_position_offset = 0
                    self.now_text_sending_failed = False
                    # if self.ser.is_open:
                    #     self.ser.close()
                    break
                else:
                    # 沒有失敗 那就繼續
                    # 總共要發送幾條
                    all_need_to_send_message_size = len(self.now_sending_text_obj.data_list)
                    # 現在發送了幾條
                    now_sent_message_size = self.now_sending_text_start_position_offset
                    if now_sent_message_size is not 0:
                        print("{0}: Now sent {1}, all {2}".format(__name__, now_sent_message_size,
                                                                  all_need_to_send_message_size))
                    if all_need_to_send_message_size - now_sent_message_size is 0:
                        # print("{0}: Msg Sent".format(__name__))
                        # 要在這邊做返回成功的消息
                        send_successful_message(self.now_sending_text_obj)
                        # 已經發完了 清除一下記錄
                        self.now_sending_text_obj = None
                        self.now_sending_text_start_position_offset = 0
                        # if self.ser.is_open:
                        #     self.ser.close()
                    else:
                        # 從候補中拿出一跳進行發送
                        now_want_to_send_message: str = self.now_sending_text_obj.data_list[now_sent_message_size]
                        # print(now_want_to_send_message)
                        # print(len(now_want_to_send_message))
                        print("{0}: Prepare to send this message:{1}".format(__name__, now_want_to_send_message))
                        start_time = time.time()
                        # 最多重新嘗試一次
                        retry_count = 3
                        is_waiting = True
                        # 準備發送
                        while is_waiting:
                            # 重試機會沒有了 清理掉
                            if retry_count == 0:
                                is_waiting = False
                                self.now_text_sending_failed = True
                            else:
                                now_want_to_send_message_bytes = now_want_to_send_message.encode('ASCII')
                                send_msg_tmp = b'at+send=lora:1:' + now_want_to_send_message_bytes + b'\r\n'
                                self.ser.write(send_msg_tmp)
                                # 從現在開始計算讀取時間
                                is_run_write_start_time = time.time()
                                is_run_write = True
                                while is_run_write:
                                    print(is_run_write_start_time)
                                    print("aaa:{0}".format(time.time()))
                                    if time.time() - is_run_write_start_time >= 30:
                                        print("超時")
                                        # 如果超時 需要扣除一次機會
                                        retry_count -= 1
                                        # 跳出循環
                                        is_run_write = False
                                    else:
                                        print("ccc:{0}".format(time.time()))
                                        lora_return = self.ser.readline()
                                        print("{0}: UART-->{1}".format(__name__, lora_return))
                                        if lora_return.startswith(b'ERROR'):
                                            retry_count -= 1
                                            is_run_write = False
                                        # elif lora_return.startswith(b'at+recv='):
                                        #     is_run_with_receive = True
                                        #     self.ser.write(b'at+send=lora:1:FF\r\n')
                                        #     while is_run_with_receive:
                                        #         _exit_txt = self.ser.readline()
                                        #         print(_exit_txt)
                                        #         if _exit_txt.startswith(b'OK\r\n'):
                                        #             is_run_with_receive = False
                                        #             print("跳出")

                                        # elif lora_return == b'[LoRa]: RUI_MCPS_UNCONFIRMED send success\r\n':
                                        elif lora_return.startswith(b'at+recv='):
                                            # 當檢測到發送成功時 自動加1準備發送下一條 q
                                            self.now_sending_text_start_position_offset += 1
                                            # 跳出本條消息的循環
                                            is_waiting = False
                                            # 跳出讀 UART的循環
                                            is_run_write = False
                                            block(0.1)
                                        print("bbb:{0}".format(time.time()))





                            # now_time = time.time()
                            # # 準備發送
                            # if retry_count == 0:
                            #     # 重試機會沒有了 清理掉
                            #     is_waiting = False
                            #     self.now_text_sending_failed = True
                            #     # if self.ser.is_open:
                            #     #     self.ser.close()
                            # else:
                            #     if now_time - start_time >= 30:
                            #         # 如果超時 需要扣除一次機會
                            #         retry_count -= 1
                            #     else:
                            #         now_want_to_send_message_bytes = now_want_to_send_message.encode('ASCII')
                            #         send_msg_tmp = b'at+send=lora:1:' + now_want_to_send_message_bytes + b'\r\n'

                                    # send_ser.write(send_msg_tmp)
                                    # #
                                    # is_run_readline = True
                                    # time_is_run_readline_start = time.time()
                                    # while is_run_readline:
                                    #     if time.time() - time_is_run_readline_start >= 15:
                                    #         is_run_readline = False
                                    #         break
                                    #     lora_return = send_ser.readline()
                                    #     print("{0}: UART-->{1}".format(__name__, lora_return))
                                    #     if lora_return == b'OK\r\n':
                                    #         # 當檢測到發送成功時 自動加1準備發送下一條 q
                                    #         self.now_sending_text_start_position_offset += 1
                                    #         # 跳出循環三次
                                    #         is_waiting = False
                                    #         send_ser.close()
                                    #         # 休息一下
                                    #         # time.sleep(0.10)
                                    # time.sleep(10000000)
                                    # # elif lora_return == b'String over max length <256 Bytes>.\r\n':
                                    # #     print("Send failed")
                                    # #     retry_count -= 1
                                    # block(100)


def start_lora_forwarder():
    lora = LoraHandleClass()
    lora.lora_init()
    lora.start_lora()
