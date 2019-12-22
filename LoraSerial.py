import serial
import Sender
import time
import LoRaTextObject

from multiprocessing import Queue

LORA_RESET_TIME_OUT = 60  # s


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
            self.ser.close()
            if not is_reset_successful:
                self.lora_init()
            print("{0}: reset lora successful".format(__name__))

    def start_lora(self):
        while True:
            # 先判斷是否有剩下沒發送的
            if self.now_sending_text_obj is None:
                # 沒有剩下的 需要從隊列中拉一個來
                if not Sender.request_send_queue.empty():
                    self.now_sending_text_obj = Sender.request_send_queue.get(block=True, timeout=None)
            else:
                # 這邊要執行發送任務
                if self.now_text_sending_failed:
                    # 不用繼續發送了 已經失敗 報告失敗
                    # 發送失敗消息
                    print("{0}: Msg send failed".format(__name__))
                    self.now_sending_text_obj = None
                    self.now_sending_text_start_position_offset = 0
                    self.now_text_sending_failed = False
                else:
                    # 沒有失敗 那就繼續
                    # 總共要發送幾條
                    all_need_to_send_message_size = len(self.now_sending_text_obj.data_list)
                    # 現在發送了幾條
                    now_sent_message_size = self.now_sending_text_start_position_offset
                    print("{0}: Now sent {1}, all {2}".format(__name__, now_sent_message_size,
                                                             all_need_to_send_message_size))
                    if all_need_to_send_message_size - now_sent_message_size is 0:
                        # 已經發完了 清除一下記錄
                        self.now_sending_text_obj = None
                        self.now_sending_text_start_position_offset = 0
                        # 要在這邊做返回成功的消息
                        print("{0}: Msg Sent".format(__name__))
                    else:
                        # 從候補中拿出一跳進行發送
                        now_want_to_send_message: str = self.now_sending_text_obj.data_list[now_sent_message_size]
                        # print(now_want_to_send_message)
                        # print(len(now_want_to_send_message))
                        print("{0}: Prepare to send this message".format(__name__))
                        start_time = time.time()
                        # 最多重新嘗試一次
                        retry_count = 3
                        is_waiting = True
                        while is_waiting:
                            now_time = time.time()
                            # 準備發送
                            if retry_count == 0:
                                # 重試機會沒有了 清理掉
                                is_waiting = False
                                self.now_text_sending_failed = True
                                if self.ser.is_open:
                                    self.ser.close()
                            else:
                                if now_time - start_time >= 30:
                                    # 如果超時 需要扣除一次機會
                                    retry_count -= 1
                                else:
                                    if not self.ser.is_open:
                                        self.ser.open()
                                    now_want_to_send_message_bytes = now_want_to_send_message.encode('ASCII')
                                    self.ser.write(b'at+send=lora:2:' + now_want_to_send_message_bytes + b'\r\n')
                                    lora_return = self.ser.readline()
                                    if lora_return == b'[LoRa]: RUI_MCPS_UNCONFIRMED send success\r\n':
                                        # 當檢測到發送成功時 自動加1準備發送下一條
                                        self.now_sending_text_start_position_offset += 1
                                        # 跳出循環三次
                                        is_waiting = False
                                        # 休息一下
                                        time.sleep(0.05)
                                    print("{0}: UART-->{1}".format(__name__, lora_return))
                        # 判斷這個封包有沒有發送成功， 發送成功則切換到下一個








                # print("bbbbb")
                # print(self.now_sending_text_obj.raw)
                # print(len(self.now_sending_text_obj.raw))
                # print(struct.pack("B", 255))

            # 判斷進入隊列中是否有元素

            # time.sleep(1)


def start_lora_forwarder():
    lora = LoraHandleClass()
    lora.lora_init()
    lora.start_lora()
