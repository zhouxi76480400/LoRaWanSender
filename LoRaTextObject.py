import RandomGenerator
import Sender
import math
import struct

# 自定義封包的前面留出的兩個0-255的byte 第一個byte說明這是第幾條 後一個byte說明一共有幾條
LORA_PACKET_SPLIT_PREFIX_LENGTH = 2

# 後面加的唯一碼 unique_code 就是 這條消息的名字 比如 a0f3 f134
LORA_PACKET_SPLIT_SUFFIX_LENGTH = 2


class LoRaTextObject:
    # 要傳輸的數據的本體，已經加好頭和尾，也分成一個包的大小了
    data_list: list
    # 唯一的識別碼
    unique_code: str

    raw: bytes

    def __init__(self, _data: bytes):
        # self.data = _data
        self.data_list = []
        self.raw = _data
        self.unique_code = RandomGenerator.generate_code_4_length()
        self.split()

    def hex_to_byte_list(self, in_str):
        bytes_array = []
        hex_str = ''.join(in_str.split(" "))
        for i in range(0, len(hex_str), 2):
            bytes_array.append(int(hex_str[i:i + 2], 16).to_bytes(length=1, byteorder='big'))
        return bytes_array

    def split(self):
        # 每個包真實的長度
        true_packet_length = (Sender.LORA_PACKET_MAX_BYTE_LENGTH -
                              LORA_PACKET_SPLIT_PREFIX_LENGTH - LORA_PACKET_SPLIT_SUFFIX_LENGTH)
        raw_message_length = len(self.raw)
        # 向上取整數,算出需要幾條
        all_msg_size = math.ceil(raw_message_length / true_packet_length)
        for i in range(all_msg_size):
            # 開始取值的下標
            start_position = i * true_packet_length
            # 停止取值的下標
            stop_position = true_packet_length
            # 如果是最後一個包可能是不滿的
            if i is all_msg_size - 1:
                last_packet_true_length = raw_message_length % true_packet_length
                stop_position = last_packet_true_length
            stop_position += start_position
            # 從源中取值
            split_raw = self.raw[start_position:stop_position]
            # 生成前綴的頭和尾
            prefix_1: bytes = struct.pack("B", i+1)
            prefix_2: bytes = struct.pack("B", all_msg_size)
            # 生成後綴
            suffix: bytes = self.hex_to_byte_list(self.unique_code)[0] + self.hex_to_byte_list(self.unique_code)[1]
            new_msg_split_64_byte = prefix_1 + prefix_2 + split_raw + suffix
            self.data_list.append(new_msg_split_64_byte)


# 生成object
def get_a_lora_txt_object(data):
    obj: LoRaTextObject = LoRaTextObject(data)
    return obj
