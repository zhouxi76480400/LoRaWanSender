import socket

tcpServerSocket=socket.socket()#创建socket对象
host = socket.gethostname()#获取本地主机名
port=1700#设置端口
tcpServerSocket.bind((host,port))#将地址与套接字绑定，且套接字要求是从未被绑定过的
tcpServerSocket.listen(5)#代办事件中排队等待connect的最大数目
while True:
    #建立客户端连接,接受connection，返回两个参数，c是该connection上可以发送和接收数据的新套接字对象
    #addr是与connection另一端的套接字绑定的地址
    c, addr = tcpServerSocket.accept()
    print ('连接地址：', addr)
    str='来自服务端的消息！'
    c.send(str)
    #套接字在垃圾收集garbage-collected时会自动close
    #close关闭该connection上的资源但不一定马上断开connection
    #想要立即断开connection，要先调用shutdown再close
    c.close() # 关闭连接