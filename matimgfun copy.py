from threading import Thread
import time
import cv2
import numpy as np
import traceback
from multiprocessing import Process, Pipe


def Mat_spawn(f):
    def fun(pipe, x, y,i,j):
        pipe.send((x,y,f(i, j).download()))
        pipe.close()
    return fun


def parmap(args):
    pipe = [Pipe() for x in range(len(args))]
    # if len(args) != 8:
    #     return None
    proc = [Process(target=Mat_spawn(z), args=(c, x, y,i,j))
            for (x, y,z,i,j), (p, c) in zip(args, pipe)]
    [p.start() for p in proc]
    [p.join() for p in proc]
    return tuple([p.recv() for (p, c) in pipe])

# if __name__ == '__main__':
#     print parmap(lambda x: x**x, range(1, 5))


class WorkingThread(Thread):
    """docstring for UploadThread."""

    def __init__(self, func, arg):
        super(WorkingThread, self).__init__()
        self.func = func
        self.arg = arg

    def run(self):
        self.result = self.func(self.arg)

    def get_result(self):
        try:
            return self.result
        except:
            print(traceback.format_exc())
            return None


class Working2Thread(Thread):
    """docstring for UploadThread."""

    def __init__(self, func, args):
        super(Working2Thread, self).__init__()
        self.func = func
        self.arg = args
        self.result = None

    def run(self):
        self.result = self.arg[0], self.arg[1], self.func(
            self.arg[2], self.arg[3]).download()

    def get_result(self):
        try:
            if self.result is not None:
                return self.result
        except:
            print(traceback.format_exc())
            return None


class MatImgs(object):
    """docstring for MatImgs."""

    def __init__(self, samples):
        super(MatImgs, self).__init__()
        self.rawsamples = samples
        self.samples = tuple([x for x in enumerate(samples)])
        self.sample_shapes = tuple([(x.shape[0], x.shape[1])
                                    for x in self.rawsamples])
        self.Gpuframe = cv2.cuda_GpuMat()
        self.CreateGpumem()
        self.TemplateMatching = None
        # self.CreateTemplateMat()
        self.hashFun = cv2.img_hash.PHash_create()

    def CreateGpumem(self):
        self.GpuMatMem = tuple([(i[0], cv2.cuda_GpuMat())
                               for i in self.samples])
        [x[1].upload(y) for x, y in zip(self.GpuMatMem, self.rawsamples)]

    def CreateTemplateMat(self, number=None, method=cv2.TM_SQDIFF_NORMED):
        if number and number != 0 and type(number) is int:
            self.TemplateMatching = tuple([cv2.cuda.createTemplateMatching(
                cv2.CV_8UC1, method) for i in range(number)])
        else:
            self.TemplateMatching = tuple([cv2.cuda.createTemplateMatching(
                cv2.CV_8UC1, method) for i in self.rawsamples])

    def M_ready(self, frames):
        Number = len(frames)
        # startCreatemattime = time.time()
        self.CreateTemplateMat(Number)
        # endCreatemattime = time.time()
        # print("create mat time : ", endCreatemattime-startCreatemattime)

        # startInputGpumemtime = time.time()
        self.Gpuframe = [(i, cv2.cuda_GpuMat()) for i in range(Number)]
        [i[1][1].upload(i[0][2]) for i in zip(frames, self.Gpuframe)]
        # endInputGpumemtime = time.time()
        # print("gpu upload time : ", endInputGpumemtime-startInputGpumemtime)
        self.frames = frames

    def Mt_ready(self, frames):
        Number = len(frames)
        startCreatemattime = time.time()
        self.CreateTemplateMat(Number)
        endCreatemattime = time.time()
        print("create mat time : ", endCreatemattime-startCreatemattime)

        startInputGpumemtime = time.time()
        self.Gpuframe = tuple([(i, cv2.cuda_GpuMat()) for i in range(Number)])
        # [ i[1][1].upload(i[0][2])  for i in zip(frames,self.Gpuframe)]
        Uploadthreads = tuple([WorkingThread(i[1][1].upload, i[0][2])
                              for i in zip(frames, self.Gpuframe)])
        [i.start() for i in Uploadthreads]
        [i.join() for i in Uploadthreads]
        endInputGpumemtime = time.time()
        print("gpu upload time : ", endInputGpumemtime-startInputGpumemtime)
        self.frames = frames

    def M_run(self):
        def roiimg(framedata, res, Id):
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            return framedata[min_loc[1]: min_loc[1]+self.sample_shapes[Id]
                             [0], min_loc[0]:min_loc[0]+self.sample_shapes[Id][1]]

        def pHashcheck(framedata, roiimg):
            hashA, hashB = self.hashFun.compute(
                framedata), self.hashFun.compute(roiimg)
            return self.hashFun.compare(hashA, hashB)

        if self.TemplateMatching is None:
            print("please run M_ready")
            return "please run M_ready"
        # startRuntime = time.time()
        # gresults = tuple([(i[0],x[1][0],(x[0].match(i[1], x[1][1])).download())
        #                   for i in self.Gpuframe
        #                  for x in zip(self.TemplateMatching, self.GpuMatMem)])
        gresults = tuple([(i[0], x[1][0], (x[0].match(i[1], x[1][1])).download())
                         for x in zip(self.TemplateMatching, self.GpuMatMem) for i in self.Gpuframe ])
        # endRuntime = time.time()
        # print("GPU runing time : ", endRuntime-startRuntime)

        # startDownloadtime = time.time()
        # [ i[2].download() for i in gresults]
        # endDownloadtime = time.time()
        # print("download time : ",endDownloadtime-startDownloadtime)
        # ress = tuple([pHashcheck(roiimg(i[1].download(), i[0]))
        #              for i in gresults])

    def Mthreads_run(self):
        if self.TemplateMatching is None:
            print("please run M_ready")
            return "please run M_ready"
        startRuntime = time.time()
        # gresults = tuple([(i[0],x[1][0],(x[0].match(i[1], x[1][1])).download())
        #                   for i in self.Gpuframe
        #                  for x in zip(self.TemplateMatching, self.GpuMatMem)])
        gresulthreads = tuple([(i[0], x[1][0], x[0].match, i[1], x[1][1])
                               for i in self.Gpuframe
                               for x in zip(self.TemplateMatching, self.GpuMatMem)])
        gresulthreads = tuple([ gresulthreads[i:i+1] for i in range(0,len(gresulthreads),1)])
        
        test = [  parmap(i)  for i in gresulthreads ]
        # gresults =  [x.get_result() for x in gresulthreads ]
        endRuntime = time.time()
        print("GPU runing time : ", endRuntime-startRuntime)

    def S_ready(self,Number=None):
        self.CreateTemplateMat(number=Number)

    def S_Matimg_run(self, framedata):
        if self.TemplateMatching is None:
            self.CreateTemplateMat()

        def roiimg(res, Id):
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            return framedata[min_loc[1]: min_loc[1]+self.sample_shapes[Id]
                             [0], min_loc[0]:min_loc[0]+self.sample_shapes[Id][1]]

        def pHashcheck(roiimg):
            hashA, hashB = self.hashFun.compute(
                framedata), self.hashFun.compute(roiimg)
            return self.hashFun.compare(hashA, hashB)

        self.Gpuframe.upload(framedata)

        gresults = tuple([(x[1][0], x[0].match(self.Gpuframe, x[1][1]).download())
                         for x in zip(self.TemplateMatching, self.GpuMatMem)])
        # ress = tuple([pHashcheck(roiimg(i[1].download(), i[0]))
        #              for i in gresults])
        # print(ress)


def main():

    img1 = cv2.imread("uniclass2200319/demo_img/back.png")
    if not np.max(img1):
        return False
    imgs = (cv2.imread("uniclass2200319/demo_img/sample1.png"), cv2.imread(
        "uniclass2200319/demo_img/sample2.png"), cv2.imread("uniclass2200319/demo_img/sample3.png"))
    for i in imgs:
        if not np.max(i):
            return False
    test = MatImgs(imgs)
    Strat = time.time()
    test.S_Matimg_run(img1)
    End = time.time()
    print("time :", End-Strat)


if __name__ == "__main__":
    debug = main()
    print(debug)
