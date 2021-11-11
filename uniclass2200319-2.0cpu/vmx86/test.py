import cv2
import os
import numpy as np
import time
from multiprocessing import Pool, Process
from numpy.core.arrayprint import IntegerFormat

HOME = os.getcwd()
samplefolder = f"{HOME}/multisample/mutiimg"

samples = os.listdir(samplefolder)

samplepathgen = tuple([cv2.imread(f"{samplefolder}/{i}") for i in samples])[0]

nowfolder = f"/tmp/image"

files = os.listdir(nowfolder)

filesgen = (cv2.imread(f"{nowfolder}/{i}") for i in files)

# filesgen = (cv2.imread(i) for i in filespath)
# samples = tuple(samplepathgen)


def MaTimg(img, template):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.9)
    # [cv2.rectangle(img, i, (i[0] + w, i[1] + h), 255, 1)
    #  for i in zip(*loc[::-1])]


class Matimg(object):
    def __init__(self, sample=None, samples=None):
        if sample is not None:
            self.sample = sample
        if samples is not None:
            self.samples = samples

    def MaTimg(self, img):
        return cv2.matchTemplate(img, self.sample, cv2.TM_CCOEFF_NORMED)
        # loc = np.where(res >= 0.9)


    def MaTimgs(self, imgs):
        # if type(imgs) is tuple :
        #     res = [cv2.matchTemplate(i, self.sample, cv2.TM_CCOEFF_NORMED) for i in imgs ]
        #     [ np.where(i >= 0.9) for i in res]
        return [cv2.matchTemplate(imgs, i, cv2.TM_CCOEFF_NORMED)
               for i in self.samples]
            # loc = np.where(res >= 0.9)



def MaTimgg(img):
    return  tuple([cv2.matchTemplate(img, i, cv2.TM_CCOEFF_NORMED)
                for i in samples])
    # loc = np.where(res >= 0.9)


def main():
    pool = Pool()
    # datas = tuple(filesgen)
    Starttime = time.time()

    # test = [ cv2.matchTemplate(i, samplepathgen, cv2.TM_CCOEFF_NORMED)  for i in filesgen ]


    # [pool.map(Matimg(i).MaTimg,datas) for i in samplepathgen ]
    test = pool.map(Matimg(sample=samplepathgen).MaTimg, filesgen)
    # tuple(map(Matimg(samples=filesgen).MaTimgs,filesgen))
    # processs = tuple([ Process(target=Matimg(i).MaTimg,args=(datas,)) for i in samplepathgen])
    # [ i.start() for i in processs]
    # [ i.join() for i in processs]
    # test =pool

    # p = Process(target=f, args=(datas,))
    # [ MaTimg(i,j) for i in filesgen for j in samplepathgen ]
    Endtime = time.time()
    print(Endtime-Starttime)
    k = [ x for x in test]
    print(len(k))    
    # Starttime = time.time()
    # pool.map(Matimg(samples=samples).MaTimgs, filesgen)
    # Endtime = time.time()
    # print(Endtime-Starttime)
if __name__ == "__main__":
    main()
