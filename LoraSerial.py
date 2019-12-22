import serial
import Sender
import time
import LoRaTextObject
import struct

from multiprocessing import Queue


class LoraHandleClass:
    lora_serial_port: str

    # 現在準備發送的object
    now_sending_text_obj: LoRaTextObject.LoRaTextObject

    # 現在這個包已經發送的offset值
    now_sending_text_start_position_offset = 0

    def __init__(self, serial_port):
        self.lora_serial_port = serial_port
        self.now_sending_text_obj = None

    def start_lora(self):
        while True:
            # 先判斷是否有剩下沒發送的
            if self.now_sending_text_obj is None:
                # 沒有剩下的 需要從隊列中拉一個來
                if not Sender.request_send_queue.empty():
                    self.now_sending_text_obj = Sender.request_send_queue.get(block=True, timeout=None)
            else:
                # 這邊要執行發送任務
                # 總共要發送幾條
                all_need_to_send_message_size = len(self.now_sending_text_obj.data_list)
                # 現在發送了幾條
                now_sent_message_size = self.now_sending_text_start_position_offset
                if all_need_to_send_message_size - now_sent_message_size is 1:
                    # 已經發完了 清除一下記錄
                    self.now_sending_text_obj = None
                    self.now_sending_text_start_position_offset = 0
                    # 要在這邊做返回消息
                else:
                    # 從候補中拿出一跳進行發送
                    now_want_to_send_message = self.now_sending_text_obj.data_list[now_sent_message_size]
                    print(now_want_to_send_message)
                    print(len(now_want_to_send_message))
                    print("準備發送這條")



                # print("bbbbb")
                # print(self.now_sending_text_obj.raw)
                # print(len(self.now_sending_text_obj.raw))
                # print(struct.pack("B", 255))


            # 判斷進入隊列中是否有元素



            time.sleep(1)


def start_lora_forwarder():
    lora = LoraHandleClass(Sender.LORA_SERIAL_PORT)
    lora.start_lora()

