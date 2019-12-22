from socket import socket, AF_INET, SOCK_DGRAM
s = socket(AF_INET, SOCK_DGRAM)

test = "い"

s.sendto(bytes(test, 'utf-8'), ('localhost', 35000))
