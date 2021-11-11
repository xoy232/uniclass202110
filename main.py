from multiprocessing.connection import Client, Listener
from lib import HOME
from threading import Thread
from strgen import StringGenerator as SG
from subprocess import Popen
import time
import argparse
import os
import traceback
from lib.pathcheck import ReadFolderFile, RmFile, RmFolder
from queue import Queue
from multiprocessing import cpu_count


def demoread():
    import os
    import cv2
    import numpy as np
    # 讀檔
    nowfolder = f"/tmp/image"
    files = os.listdir(nowfolder)
    framelist = (cv2.imread(f"{nowfolder}/{i}", 0) for i in files)
    framelist = tuple([i for i in framelist if np.max(i)])
    # 讀sample
    # samplepath = os.listdir(f"{HOME}/mutiimg")
    # sampleimgs = (cv2.imread(f'{HOME}/mutiimg/{i}', 0) for i in samplepath)
    # samplelen = len((sampleimgs[0],))
    # sampleimgs = tuple([i for i in sampleimgs if np.max(i)])
    return framelist


def readsamplepath(samplefolder):
    filespath = os.listdir(samplefolder)
    return (f'{samplefolder}/{i}' for i in filespath)


class UseServerThread(Thread):
    """docstring for CreateServerThread."""

    def __init__(self, frames, queue, Bashcmd, Path, Key, Door=False, delaytime=15):
        super(UseServerThread, self).__init__()
        self.frames = frames
        self.queue = queue
        self.Path = Path
        self.Key = Key
        self.delaytime = delaytime
        self.Bashcmd = Bashcmd
        self.Door = Door
        self.Create_Process()

    def Create_Process(self):
        self.Pro = Popen(self.Bashcmd)
        time.sleep(self.delaytime)

    def run(self) -> None:
        # testframes = demoread()
        # self.frames = testframes
        if self.frames is False:
            self.CloseMsg()
            self.queue.put(False)
            return super().run()
        elif self.frames is None:
            self.queue.put(None)
            return super().run()

        with Client(self.Path, authkey=(self.Key).encode()) as conn:
            try:
                conn.send((0, self.frames))
                self.queue.put(conn.recv())
                conn.send(0)
            except:
                pass
        if self.Door is False:
            self.CloseMsg()
        return super().run()

    def CloseMsg(self):
        try:
            with Client(self.Path, authkey=(self.Key).encode()) as conn:
                conn.send(0)
        except:
            pass


def CreateBash(FILE, key, folder, samplepath, Process, Name, delay):
    RmFolder(folder)
    try:
        os.mkdir(folder)
    except:
        pass

    raw_bash = ['python3', FILE]
    if key:
        if type(key) is str:
            raw_bash = raw_bash + ["-K"]+[key]
    if folder and type(folder) is str:
        raw_bash = raw_bash + ["-F"]+[folder]
    if samplepath and type(samplepath) is str:
        raw_bash = raw_bash + ["-S"]+[samplepath]
    if Process and type(Process) is str:
        raw_bash = raw_bash + ["-P"]+[Process]
    if Process and type(Name) is str:
        raw_bash = raw_bash + ["-N"]+[Name]
    if delay:
        if type(delay) is int:
            raw_bash = raw_bash + ["-D"]+[str(delay)]
        elif type(delay) is str:
            raw_bash = raw_bash + ["-D"]+[delay]
    return raw_bash


def get_parser():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-P', '--process', type=str,
                        default=str(cpu_count()))
    parser.add_argument('-D', '--delaytime', type=int,
                        default=6)
    parser.add_argument('-G', '--globaldelaytime', type=int,
                        default=15)
    parser.add_argument('-K', '--key', type=str,
                        default="secret password")
    parser.add_argument('--serverpath', type=str,
                        default="/tmp/servertest")
    group.add_argument('-S', '--sample', type=str
                    #    , default="/home/nvidia/works/uniclass202110/mutiimg/1.png"
                       )
    group.add_argument('--samplespath', type=str
                          , default="/home/nvidia/works/uniclass202110/mutiimg"
                       )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    SERVERPATH = args.serverpath
    RmFile(SERVERPATH)
    PROCESS = args.process
    KEY = args.key
    DELAYTIME = args.delaytime
    GDELAYTIME = args.globaldelaytime
    QUE = Queue()
    if args.sample:
        TYPE = 0
        sample = args.sample
        with Listener(SERVERPATH, authkey=KEY.encode()) as listener:
            try:
                RandomName = SG(r'[\w]{10}').render()
                Folderpath = f"/tmp/{RandomName}"
                RmFolder(Folderpath)
                serverpath = f"{Folderpath}/{RandomName}"
                bashcmd = CreateBash(Name=RandomName, folder=Folderpath, samplepath=sample, Process=PROCESS,
                                     FILE=f"{HOME}/bin/run.muti.py", key=KEY, delay=DELAYTIME)
                P = Popen(bashcmd)
                if P and P.poll() is not None:
                    print(-1)
                    return -1
                Door = True
                time.sleep(GDELAYTIME)
                # client = Client(serverpath, authkey=(KEY).encode())
                with Client(serverpath, authkey=(KEY).encode()) as client:
                    while Door:
                        try:
                            with listener.accept() as conn:
                                while True:
                                    if P and P.poll() is not None:
                                        Door = False
                                        try:
                                            conn.recv()
                                            conn.send(-1)
                                            client.send(0)
                                        except:
                                            pass
                                        break
                                    try:
                                        Msg = conn.recv()
                                        if type(Msg) is tuple:
                                            client.send((0, Msg))
                                            conn.send(client.recv())
                                        elif type(Msg) is int and Msg == 0:
                                            client.send(0)
                                            Door = False
                                            break
                                        else:
                                            conn.send(-1)
                                    except KeyboardInterrupt:
                                        client.send(0)
                                        Door = False
                                        break
                                    except EOFError:
                                        print(
                                            f"main server  {SERVERPATH} :  {listener.last_accepted} will be disconnected")
                                        break
                                    except ConnectionResetError:
                                        print(
                                            f"main server  {SERVERPATH} :  {listener.last_accepted} will be disconnected")
                                        break
                                    except BrokenPipeError:
                                        print(
                                            f"main server  {SERVERPATH} :  {listener.last_accepted} will be disconnected")
                                        break
                                    except:
                                        try:
                                            client.send(0)
                                        except:
                                            pass
                                        Door = False
                                        print("mainserver error : ",
                                              traceback.format_exc())
                                        break
                        except KeyboardInterrupt:
                            try:
                                client.send(0)
                            except:
                                pass
                            Door = False
            finally:
                time.sleep(3)
                if P and P.poll() is None:
                    P.kill()
                RmFolder(Folderpath)
            # RmFile(SERVERPATH)

    elif args.samplespath:
        
        samplepath = readsamplepath(args.samplespath)
        if os.path.isdir(samplepath):
            filespath = tuple(ReadFolderFile(samplepath))
            with Listener(SERVERPATH, authkey=KEY.encode()) as listener:
                while Door:
                    with listener.accept() as conn:
                        for i in filespath :
                            pass
        else :
            print("not found folder")

    # frames = readsample()


if __name__ == "__main__":
    main()
