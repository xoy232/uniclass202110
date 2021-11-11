#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import socket
import numpy as np
import struct

HOST = '192.168.55.1'
PORT = 9000


class Server(object):
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, PORT))
        self.s.listen(5)
        print('server start at: %s:%s' % (HOST, PORT))
        print('wait for connection...')

    def connect(self):
        conn, addr = self.s.accept()
        print('connected by ' + str(addr))
        return conn, addr

    def takeing(self, *, conn, data=None, TYPE=None):
        def image(con):
            def recvall(sock, count):
                buf = b''
                while count:
                    newbuf = sock.recv(count)
                    if close(newbuf) is False:
                        return False
                    if not newbuf:
                        return None
                    buf += newbuf
                    count -= len(newbuf)
                return buf
            try:
                length = recvall(con, 16)
                if length is False:
                    return False
                stringData = recvall(con, int(length))
                if stringData is False:
                    return False
                data = np.fromstring(stringData, dtype='uint8')
                decimg = cv2.imdecode(data, 1)
                if np.max(decimg):
                    return decimg
            except:
                conn.close()
                print('get image error ! client closed connection.')
                return False

        def send(data):
            try:
                print("send:"+data)
                data = data.encode()
                bytes_len = struct.pack('i', len(data))
                conn.send(bytes_len)
                conn.send(data)
            except:
                conn.close()
                print('send error so client closed connection.')
                return False

        def Getdata():
            try:
                bytes_len = conn.recv(4)
                if close(bytes_len) is False:
                    return False
                msg_len = struct.unpack('i', bytes_len)[0]
                msg = conn.recv(msg_len)
                if close(msg) is False:
                    return False
                msg = msg.decode()
                print("recv: ", msg)
                return msg
            except:
                conn.close()
                print('getdata error so client closed connection.')
                return False

        def close(raw_indata):
            if len(raw_indata) == 0:
                conn.close()
                print('client closed connection.')
                return False

        message = Getdata()
        if message == "send_image" and TYPE == "send_image":
            send("waiting!")
            decimg = image(conn)
            return decimg

        elif message == "send_frame" and TYPE == "send_frame":
            send("waiting!!")
            decimg = image(conn)
            return decimg

        elif message == "report" and TYPE == "report":
            send(data)
        elif message is False:
            return False


if __name__ == "__main__":
    pass
    # server = Server()
    # while True:
    #     conn, addr = server.connect()
    #     while True:

    #         data = server.takeing(conn=conn)
    #         print("data= ", data, "\n")
    #         print("type data=", type(data), "\n")
    #         if data is False:
    #             break
