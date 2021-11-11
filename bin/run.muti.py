from subprocess import Popen
from multiprocessing.connection import Client,Listener
import threading
import argparse
import traceback
from queue import Queue
from lib import HOME
import numpy as np
import time
from lib.pathcheck import RmFile

FILE = f"{HOME}/bin/Matimgfun.py"

# DEMOTEST = SG(r"[\w]{30}").render()
DEMOTEST = "demotest"
# DEMOTEST = "lLzrfMbvkCA6k_MSqJo3kbDbD3uHSL"


def run_child_process(Name, M_process=None, key=None, samplepath=None, folder=None):
    raw_bash = ['python3', FILE]
    if key and type(key) is str:
        raw_bash = raw_bash + ["-K"]+[key]
    if folder and type(folder) is str:
        raw_bash = raw_bash + ["-F"]+[folder]
    if samplepath and type(samplepath) is str:
        raw_bash = raw_bash + ["-S"]+[samplepath]
    if M_process is None:
        return raw_bash, Popen(raw_bash)
    else:
        if type(M_process) is int:
            # RandomName = SG(r'[\w]{5}').render()
            return tuple([(f"{folder}/{Name}{i}", Popen(raw_bash + ["-N"]+[Name+str(i)])) for i in range(M_process)])


class MatClient(threading.Thread):
    """docstring for MakeProcess."""

    def __init__(self, q, client, Type=0, frames=None, frame=None):
        super(MatClient, self).__init__()
        # self.Name = Name
        self.queue = q
        if not frames is None:
            self.frames = frames
        if not frame is None:
            self.frame = frame
        self.client = client
        self.Type = Type

    def run(self) -> None:
        datas = None
        if self.Type == 0:
            try:
                while datas is None:
                    Msg = self.client.recv()
                    if self.frames:
                        if Msg == 1:
                            self.client.send(self.frames)
                        elif Msg and type(Msg) is tuple:
                            datas = Msg
                            self.queue.put(datas)
                else:
                    self.frames = None
                    # client.recv()
            except:
                print("WHAT!!!!!!!", traceback.format_exc())
                try:
                    self.client.close()
                except:
                    pass
                self.queue.put(False)
        if self.Type == 1:
            try:
                while True:
                    Msg = self.client.recv()
                    if Msg == 2 and self.sample is not None and np.max(self.sample):
                        self.client.send(self.sample)
                        break
                    elif Msg == 1:
                        self.client.send(1)
            except:
                print("WHAT!!!!!!!", traceback.format_exc())
                try:
                    self.client.close()
                except:
                    pass
                self.queue.put(False)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--process', type=int,
                        default=2)
    parser.add_argument('-F', '--folder', type=str,
                        default="/tmp")
    parser.add_argument('-N', '--name', type=str,
                        default=DEMOTEST)
    parser.add_argument('-K', '--key', type=str,
                        default="secret password")
    parser.add_argument('-S', '--sample', type=str, default="/home/nvidia/works/uniclass202110/mutiimg/1.png"
                        )
    parser.add_argument('-D', '--delaytime', type=int, default=5
                        )
    return parser


# def readsample():
#     import os
#     import cv2
#     import numpy as np

#     # 讀檔
#     nowfolder = f"/tmp/image"
#     files = os.listdir(nowfolder)
#     framelist = (cv2.imread(f"{nowfolder}/{i}", 0) for i in files)
#     framelist = tuple([i for i in framelist if np.max(i)])
#     # 讀sample
#     samplepath = os.listdir(f"{HOME}/mutiimg")
#     sampleimgs = (cv2.imread(f'{HOME}/mutiimg/{SG(r"[\w]{30}").render()}', 0) for i in samplepath)
#     # samplelen = len((sampleimgs[0],))
#     sampleimgs = tuple([i for i in sampleimgs if np.max(i)])
#     return sampleimgs, framelist


def Global_server(NAME, KEY, QUEUE, Clients):
    Door = True
    frames = None

    def MsgRecvSend(frames):
        local_threads = tuple(
            [MatClient(q=QUEUE, client=i, frames=frames) for i in Clients])
        [i.start() for i in local_threads]

        [i.join() for i in local_threads]

        return tuple([QUEUE.get() for i in local_threads])

    with Listener(NAME, authkey=KEY.encode()) as listener:
        print(f"Global match server  {NAME} :   is ready!")
        while Door:
            with listener.accept() as conn:
                try:
                    print(
                        f"  {NAME} :  {listener.last_accepted} is connecting")
                    while True:
                        frames = None
                        raw_msg = conn.recv()
                        if type(raw_msg) is tuple:
                            if type(raw_msg[0]) is int and raw_msg[0] == 0:
                                frames = raw_msg[1]
                        elif type(raw_msg) is int:
                            if raw_msg == 0:
                                Door = False
                                print(f"match server  {NAME} is closed")
                                break
                        else:
                            conn.send(-1)
                            continue
                        del raw_msg
                        if type(frames) is tuple:
                            conn.send(MsgRecvSend(frames=frames))
                except ConnectionResetError:
                    print(
                        f"match server  {NAME} :  {listener.last_accepted} will be disconnected")
                except EOFError:
                    print(
                        f"match server  {NAME} :  {listener.last_accepted} will be disconnected")
                except BrokenPipeError:
                    print(
                        f"match server  {NAME} :  {listener.last_accepted} will be disconnected")
                except:
                    print(
                        f"[match server  {NAME}  Global error and will be disconnected ] :", traceback.format_exc())
                    break
        [i.close() for i in Clients]


def Create_Process(NAME, PROCESS, FOLDER, KEY, SAMPLE, delay=2):
    clients = None
    delay = delay
    while True:
        raw_Processes = run_child_process(
            Name=NAME, M_process=PROCESS, folder=FOLDER, samplepath=SAMPLE, key=KEY)
        namepath, Processes = tuple(zip(*raw_Processes))
        time.sleep(delay)
        [i.kill() for i in Processes if i and i.poll() is not None]
        try:
            clients = tuple([Client(i, authkey=KEY.encode()) for i in namepath])
        except:
            [i.terminate()for i in Processes if i]
            if namepath:
                for i in namepath:
                    RmFile(i)
            if delay > 10:
                return -1, -1
            delay += 1
        else:
            if Processes and clients:
                return Processes, clients
            else:
                for i in clients:
                    try:
                        i.close()
                    except:
                        pass
                [i.kill() for i in Processes if i]
                if namepath:
                    for i in namepath:
                        RmFile(i)
                if delay > 10:
                    return -1, -1
                delay += 1


# def debug():
#     return readsample()


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.sample:
        SAMPLEPATH = args.sample
    else:
        SAMPLEPATH = None
    PROCESS = args.process
    FOLDER = args.folder
    NAME = args.name
    KEY = args.key
    DELAYTIME = args.delaytime
    q = Queue()
    globalpath = f'{FOLDER}/{NAME}'
    # test
    # samples, frames = debug()

    # FILENAME = f'{FOLDER}/{NAME}'
    Processes, clients = Create_Process(
        NAME=NAME, PROCESS=PROCESS, FOLDER=FOLDER, KEY=KEY, SAMPLE=SAMPLEPATH,delay=DELAYTIME)
    if Processes == -1 or clients == -1:
        print(-1)
        return -1
    Global_server(NAME=globalpath, KEY=KEY, QUEUE=q, Clients=clients)
    time.sleep(1)
    [i.kill() for i in Processes if i]


    # try:
    # threads = tuple([MatClient(q=q, client=i, sample=samples[0],
    #    frames=frames) for i in clients])
    # [i.start() for i in threads]
    # [i.join() for i in threads]
    # except:
    # print(traceback.format_exc())
    # finally:
    # try:
    # [i.close() for i in clients]
    # except:
    # pass
    # try:
    # [i.kill() for i in Processes if i]
    # except:
    # pass
    # print([q.get() for i in threads])
    # time.sleep(5)
    # [  ([i.kill() for i in Processes if i and i.poll() is None])   for i in rawdatas  if i is False ]
    # K_Client("/tmp/Matchdemo")
if __name__ == "__main__":
    main()
