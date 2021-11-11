import time
import cv2
import numpy as np
import traceback
from threading import Thread
import os




class Working2Thread(Thread):
    """docstring for UploadThread."""

    def __init__(self, func, args,sample):
        super(Working2Thread, self).__init__()
        self.func = func
        self.arg = args
        self.sample = sample
        self.result = None
        # self.Gpuframe = cv2.cuda_GpuMat()
        # self.TemplateMatching = None
        # self.CreateGpumem()

    # def CreateGpumem(self):
    #     self.GpuMatMem = tuple([(i[0], cv2.cuda_GpuMat())
    #                            for i in self.samples])
    #     [x[1].upload(y) for x, y in zip(self.GpuMatMem, self.rawsamples)]

    def run(self):
        Gpuframe = cv2.cuda_GpuMat()
        Gpuframe.upload(self.arg)
        self.result = self.func(
            Gpuframe, self.sample)

    def get_result(self):
        try:
            if self.result is not None:
                return self.result
        except:
            print(traceback.format_exc())
            return None


def readsample(path):
    files = os.listdir(path)
    return tuple([f"{path}/{i}" for i in files])


def main():
    HOME = os.getcwd()
    # 讀檔
    nowfolder = f"/tmp/image"
    files = os.listdir(nowfolder)
    framelist = tuple([cv2.imread(f"{nowfolder}/{i}") for i in files])
    
    # 讀sample
    samplepath = readsample(f"{HOME}/mutiimg")
    sampleimgs = [cv2.imread(i) for i in samplepath]
    samplelen = len((sampleimgs[0],))
    sampleimgs = tuple([i for i in sampleimgs if np.max(i)])

    # sample存取至gpu
    # GpuMatMem = tuple([(cv2.cuda_GpuMat())
    #                    for i in range(samplelen)])
    # [x.upload(y) for x, y in zip(GpuMatMem, (sampleimgs[0],) )]
    
    GpuMatMem = cv2.cuda_GpuMat()
    
    GpuMatMem.upload(sampleimgs[0])
    
    TemplateMatching = cv2.cuda.createTemplateMatching(
                cv2.CV_8UC3, cv2.TM_SQDIFF_NORMED)
    
    # TemplateMatching = tuple([cv2.cuda.createTemplateMatching(
    #             cv2.CV_8UC1, cv2.TM_SQDIFF_NORMED) for i in range(samplelen)])
    
    gresultsthreads = tuple([ Working2Thread(func=TemplateMatching.match,args=i,sample=GpuMatMem)
        # for x,y in zip(TemplateMatching, GpuMatMem)
        for i in framelist[0:3]
    ])
    # [ i.start().join() for i in gresultsthreads]
    for i in gresultsthreads :
        i.start()
        i.join()
    # [ i.join() for i in gresultsthreads]




# def spawn(f):
#     def fun(pipe, x):
#         pipe.send(f(x))
#         pipe.close()
#     return fun
# def parmap(f,args):
#     pipe = [Pipe() for x in range(len(args))]
#     if len(args) != 8 :
#         return None
#     proc = [Process(target=spawn(f), args=(c, x)) for x, (p, c) in zip(args, pipe)]
#     [p.start() for p in proc]
#     [p.join() for p in proc]
#     return tuple([p.recv() for (p, c) in pipe])
# def test(f,X):
#     print("f:",f(4),"X:",X)
if __name__ == '__main__':
    main()
    # print(parmap(lambda x: x**x, range(1, 5)))
    # print(test(lambda x: x**x, range(1, 5)))
