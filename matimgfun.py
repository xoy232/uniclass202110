import time
import cv2
import numpy as np



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
                cv2.CV_8UC3, method) for i in range(number)])
        else:
            self.TemplateMatching = tuple([cv2.cuda.createTemplateMatching(
                cv2.CV_8UC1, method) for i in self.rawsamples])

    def S_ready(self, Number=None):
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
