#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import socket
import numpy as np
import struct


class Clientmanger(object):
    def __init__(self, *, HOST='192.168.55.1', PORT=9000, quality=100):
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

    def send_msg(self, image, TYPE=None):
        def send(data):
            try:
                print('send: ' + data)
                data = data.encode()
                bytes_len = struct.pack('i', len(data))
                self.s.send(bytes_len)
                self.s.send(data)
            except:
                self.s.close()
                print('send error maybe server closed connection.')
                return False

        def Getdata():
            def closecheck(meg):
                if len(meg) == 0:
                    self.s.close()
                    print('server closed connection.')
                    return False
            try:
                bytes_len = self.s.recv(4)
                if closecheck(bytes_len) is False:
                    return False
                msg_len = struct.unpack('i', bytes_len)[0]
                message = self.s.recv(msg_len)
                if closecheck(message) is False:
                    return False
                message = message.decode()
                print('recv: ' + message)
                return message
            except:
                self.s.close()
                print('getdata error maybe server closed connection.')
                return False
            

        outdata = TYPE
        send(outdata)
        indata = Getdata()
        if indata == "waiting!":
            if image is not None and type(image) is not str and np.max(image):
                esult, imgencode = cv2.imencode(
                    '.jpg', image, self.encode_param)
                data = np.array(imgencode)
                stringData = data.tobytes()
                self.s.send(str(len(stringData)).ljust(16).encode())
                self.s.send(stringData)
                return True
        elif indata == "waiting!!":
            if image is not None and type(image) is not str and np.max(image):
                esult, imgencode = cv2.imencode(
                    '.jpg', image, self.encode_param)
                data = np.array(imgencode)
                stringData = data.tobytes()
                self.s.send(str(len(stringData)).ljust(16).encode())
                self.s.send(stringData)
                outdata = "report"
                send(outdata)
                indata = Getdata()
                if type(indata) == str and indata:
                    cache = tuple(indata.split(','))
                    if len(cache) == 4:
                        print('recv: ', cache)
                        return cache
            else:
                send("no frame")
                return "no image"
                
        elif indata is False:
            return False

    # def send_frame(self,frame):
    #     outdata = "send_frame"
    #     print('send: ' + outdata)
    #     self.s.send(outdata.encode())
    #     indata = self.s.recv(1024)
    #     print('recv: ' + indata.decode())
    #     if frame is not None and type(frame) is not str and np.max(frame):
    #         esult, imgencode = cv2.imencode(
    #             '.jpg', frame, self.encode_param)
    #         data = np.array(imgencode)
    #         stringData = data.tobytes()
    #         self.s.send(str(len(stringData)).ljust(16).encode())
    #         self.s.send(stringData)
    #         return True
    #     else:
    #         return False

    def report(self):
        # outdata = "report"
        # print('send: ' + outdata)
        # self.s.send(outdata.encode())
        indata = self.s.recv(1024)
        print('recv: ' + indata.decode())
        if len(indata) == 0:  # connection closed
            self.s.close()
            print('server closed connection.')
            return False
        return tuple(indata.decode().split(','))


if __name__ == "__main__":
    pass
    # client = Clientmanger()
    # print(client.send_image("demo"))

    # while True :
    #     data=client.report()
