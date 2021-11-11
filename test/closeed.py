from multiprocessing.connection import Client
import time
import numpy as np
from scipy import stats

def demoread():
    import os
    import cv2
    import numpy as np
    # 讀檔
    nowfolder = f"/tmp/image"
    files = os.listdir(nowfolder)
    framelist = (cv2.imread(f"{nowfolder}/{i}", 0) for i in files)
    return tuple([i for i in framelist if np.max(i)])
    

def main():
    frames = demoread()
    timess = []
    with Client("/tmp/servertest",authkey=b"secret password") as conn :
        for i in range(100):
            Start = time.time()
            conn.send(frames)
            End = time.time()
            if not  conn.recv() is None :
                timess.append(End-Start)
            print("time : ",i+1)
        conn.send(0)
    rawtimess = timess
    timess = np.array(timess)
    print(f"mean: {np.mean(timess)}")
    print(f"stdev: {np.std(timess,ddof=1)}")
    print(f"mediam: {np.median(timess)} ")
    try :
        print(f"counts : {stats.mode(timess)[0][0]}" )
    except:
        print(f"real counts : {stats.mode(rawtimess)[0][0]}" )
    



if __name__ == "__main__":
    main()