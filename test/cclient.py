import time
import cv2
import numpy as np
from multiprocessing.connection import Client
import threading
from queue import Queue
import os


def S_Client(address, queue, sample, frames, frame=None, key=b'secret password'):
    with Client(address, authkey=key) as client:
        client.recv()
        # client.send(0)
        # return None
        client.send(sample)
        # if client.recv() == "match class is ready!" :
        print(client.recv())
        client.send(frames)

        data = client.recv()
        queue.put(data)
        client.send(00)

        print(client.recv())

        client.send(0)


def main():
    HOME = os.getcwd()
    samplefolder = f"{HOME}/mutiimg"

    samples = os.listdir(samplefolder)

    samplepathgen = tuple(
        [cv2.imread(f"{samplefolder}/{i}", 0) for i in samples])[0]

    nowfolder = f"/tmp/image"

    files = os.listdir(nowfolder)

    filesgen = tuple([cv2.imread(f"{nowfolder}/{i}", 0) for i in files])

    q = Queue()

    Start = time.time()
    t = threading.Thread(target=S_Client, args=(
        "/tmp/Matchdemo", q, samplepathgen, filesgen))
    t.start()
    t.join()

    End = time.time()
    print(End-Start)

    # for i in samplepathgen :
    #     if not type(i) is np.ndarray :
    #         print('error')
    # for i in filesgen :
    #     if not type(i) is np.ndarray :
    #         print('error')


if __name__ == "__main__":
    main()
