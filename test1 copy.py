import cv2
import numpy as np
from multiprocessing.connection import Client
from multiprocess import Pool
import time
import threading
from queue import Queue
import os

from matimgfun import MatImgs

HOME = os.getcwd()

# address = ("localhost",12000)

# for i in range(11001,11501) :
#     try :
#         with Client(("192.168.50.102",i), authkey=b'secret password') as client:
#             client.recv()
#             client.send("0")
#     except:
#         pass
def Clients(num,queue) :
    with Client(("192.168.50.102",num), authkey=b'secret password') as client:
        data = client.recv()
    queue.put(data)
# threads = []


def readsample(path):
    files = os.listdir(path)
    return tuple([ f"{path}/{i}" for i in files])





def main():
    samplepath = readsample(f"{HOME}/mutiimg")
    imgs = [ cv2.imread(i) for i in samplepath]
    imgs = [ i for i in imgs if np.max(i) ]
    # Matclass = MatImgs(imgs)
    
    # PortNumber = (  i for i in range(11001,11501) )
    # pool = Pool()
    # datas = pool.map(Clients,PortNumber)
    
    # for i in range(11001,11501):
    #     threads.append(threading.Thread(target=Clients,args=(i,)))
    q = Queue()
    threads = tuple([ threading.Thread(target=Clients,args=(i,q))  for i in range(11001,11501) ])
    [ i.start() for i in threads]
    [ i.join() for i in threads ]
    datas = tuple([ q.get() for i in threads ])
    
    datas = tuple([ (x[0],x[1],cv2.imdecode(np.frombuffer(x[2], np.uint8), -1),x[3]) for x in datas if x and len(x) == 4])
    # [ print(type(i[2])) for i in datas ]
    M_datas = tuple([ datas[i:i+125] for i in range(0,len(datas),125)])
    
    for i in range(1,len(imgs)):
        Matclass = MatImgs(imgs[0:i])
        # Matclass.S_ready()
        Strat = time.time()
        # [Matclass.S_Matimg_run(i[2]) for i in datas]
        # Matclass.M_ready(datas[:150])
        # Matclass.Mt_ready(datas[:150])
        # Matclass.Mthreads_run()
        # Matclass.M_ready(datas[51:150])
        # Matclass.M_run()
        End = time.time()
        print("Simple run","N: ",i," realtime :", End-Strat)
        # Matclass = MatImgs(imgs[0:i])
        Strat = time.time()
        # for j in M_datas :
        #     Matclass.M_ready(j)
        #     Matclass.M_run()
        End = time.time()
        print("Muti run! ","N: ",i," realtime :", End-Strat)
        # print(len(datas))
        


if __name__ == "__main__":
    Gstarttime = time.time()
    main()
    Gendtime = time.time()
    
    print(f"Gtime:  {Gendtime-Gstarttime}")
        
    
    