from random import choice


# 生成四位隨機碼
def generate_code_4_length():
    seeds = "1234567890ABCDEF"
    random_num = []
    for i in range(4):
        random_num.append(choice(seeds))
    return "".join(random_num)
