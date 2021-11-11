from subprocess import Popen
import os
from multiprocessing.connection import Client
import threading
from queue import Queue
import time
import traceback
import cv2
import random
# import gc

HOME = os.getcwd()

FILE = f"{HOME}/bin/Matimgfun.py"


def run_child_process(Name, key=None, folder=None):
    return Popen(['python3', FILE, "-N", Name])


def S_Client(address, queue, sample, frames, frame=None, key=b'secret password'):
    with Client(address, authkey=key) as client:
        client.recv()

        ##########
        # client.send(0)
        # return None
        #######
        client.send(sample)
        # if client.recv() == "match class is ready!" :
        # print(client.recv())
        client.recv()
        client.send(frames)

        data = client.recv()
        queue.put(data)
        client.send(00)

        # print(client.recv())
        client.recv()

        client.send(0)

def K_Client(address,  key=b'secret password'):
    with Client(address, authkey=key) as client:
        client.recv()

        ##########
        client.send(0)
        







def main():
    pass



def demoimg():
    samplefolder = f"{HOME}/mutiimg"

    samples = os.listdir(samplefolder)

    samplepathgen = tuple(
        [(f"{i}.pipe", cv2.imread(f"{samplefolder}/{i}", 0)) for i in samples])

    nowfolder = f"/tmp/image"

    files = os.listdir(nowfolder)

    filesgen = tuple([cv2.imread(f"{nowfolder}/{i}", 0) for i in files])
    return samplepathgen, filesgen



def testmain():
    samples, frames = demoimg()
    # samplelen = len(samples)
    # samplepaths , samples = tuple(zip(rawsamples))
    # demoname = "test1"
    for x in range(1,5):
        for xx in range(30):
            samplename , sample = random.choice(samples)
            q = Queue()
            try:
                Mat_Process = [run_child_process(samplename+str(j)) for j in range(x) ]
            except:
                print(*["#" for i in range(10)])
                print(traceback.format_exc())
                print(*["#" for i in range(10)])
            else:
                time.sleep(5)
                try:
                    # [S_Client(f"/tmp/{i}",q,j,frames) for i,j in samples]
                    Starttime = time.time()
                    threads = tuple([threading.Thread(target=S_Client, args=(
                        f"/tmp/{samplename+str(j)}", q, sample, frames)) for  j in  range(x)])
                    # del samples, frames
                    # gc.collect()
                    [i.start() for i in threads]
                    [i.join() for i in threads]
                except:
                    print(*["#" for i in range(10)])
                    print(traceback.format_exc())
                    print(*["#" for i in range(10)])
                    try :
                        tuple([threading.Thread(target=K_Client, args=(
                            f"/tmp/{samplename+str(j)}")) for  j in  range(x)])
                    except :
                        pass
                    # [x.kill() for x in Mat_Process if x and x.poll() is not None]
                    break
                else:
                    try :
                        rawdatas = tuple([ q.get() for i in threads])
                        # for i in threads:
                        #     print("*************** ",i , '***************')
                        #     print(q.get())

                        [ j for i in rawdatas for j in i]
                        Endtime = time.time()
                    except:
                        print(*["#" for i in range(10)])
                        print(traceback.format_exc())
                        print(*["#" for i in range(10)])
                        try :
                            tuple([threading.Thread(target=K_Client, args=(
                                f"/tmp/{samplename+str(j)}")) for  j in  range(x)])
                        except :
                            pass
                        # [x.kill() for x in Mat_Process if x and x.poll() is not None]
                        break
                    else :
                        # print(
                        #     f"sample : {i} N: {len(datas)}  multiprocess runtime : ", Endtime-Starttime)
                        with open(f"{HOME}/testdata_720/multesttime{x}.txt","a") as f :
                            f.write(f"{x},{(Endtime-Starttime)/(x*len(frames))}\n")

                        # print(*[ "\*" for i in range(30)])
                        # print(datas)

    try:
        [i.kill() for i in Mat_Process if i and i.poll() is not None]
    except:
        pass

# def main():
#     samples, frames = demoimg()
#     samplelen = len(samples)
#     # samplepaths , samples = tuple(zip(rawsamples))
#     # demoname = "test1"
#     for i in range(1,samplelen+1):
#         # testsample = samples[0:i]
#         q = Queue()
#         try:
#             Mat_Process = [run_child_process(i) for i, j in samples[0:i]]
#         except:
#             print(*["#" for i in range(10)])
#             print(traceback.format_exc())
#             print(*["#" for i in range(10)])
#         else:
#             time.sleep(2+i)
#             try:
#                 # [S_Client(f"/tmp/{i}",q,j,frames) for i,j in samples]
#                 Starttime = time.time()
#                 threads = tuple([threading.Thread(target=S_Client, args=(
#                     f"/tmp/{i}", q, j, frames)) for i, j in samples[0:i]])
#                 # del samples, frames
#                 # gc.collect()
#                 [i.start() for i in threads]
#                 [i.join() for i in threads]
#             except:
#                 print(*["#" for i in range(10)])
#                 print(traceback.format_exc())
#                 print(*["#" for i in range(10)])
#             else:
#                 try :
#                     rawdatas = tuple([ q.get() for i in threads])
#                     # for i in threads:
#                     #     print("*************** ",i , '***************')
#                     #     print(q.get())

#                     datas = [ j for i in rawdatas for j in i]
#                     Endtime = time.time()
#                 except:
#                     print(*["#" for i in range(10)])
#                     print(traceback.format_exc())
#                     print(*["#" for i in range(10)])
#                 else :
#                     # print(
#                     #     f"sample : {i} N: {len(datas)}  multiprocess runtime : ", Endtime-Starttime)
#                     with open("./multesttime.txt","a") as f :
#                         f.write(f"{Endtime-Starttime}\n")
                    
#                     # print(*[ "\*" for i in range(30)])
#                     # print(datas)

#     try:
#         [i.kill() for i in Mat_Process if i and i.poll() is not None]
#     except:
#         pass


if __name__ == "__main__":
    main()
