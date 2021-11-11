# import time
import cv2
import numpy as np
import traceback
# import os
from multiprocessing.connection import Listener
import argparse
from lib.pathcheck import RmFile, check_filepath

# HOME = os.getcwd()
# Door = True

# MAT = None


class MatImg(object):
    def __init__(self, sample, method=cv2.TM_CCOEFF_NORMED):
        super(MatImg, self).__init__()
        self.w, self.h = sample.shape[::-1]
        self.sample = cv2.cuda_GpuMat()
        self.sample.upload(sample)
        self.frame = cv2.cuda_GpuMat()
        self.Mat = cv2.cuda.createTemplateMatching(
            cv2.CV_8UC1, method)

    def run(self, frame, Number=None, threshold=0.9):
        self.frame.upload(frame)
        res = self.Mat.match(self.frame, self.sample).download()

        # loc = np.where(res >= threshold)
        # Target = tuple([ i for i in zip(*loc[::-1])])

        # [cv2.rectangle(frame, (x,y),(x+w,y+h),255,2) for x ,y in Target ]
        # for x ,y in Target[0:-3] :
        #     copyframe = frame.copy()
        #     sx,sy = x+self.w , y+self.h
        #     if sx > 1920 or sy >1080 :
        #         continue
        #     cv2.rectangle(copyframe, (x,y),(sx,sy),255,2)
        #     cv2.imshow('simg',copyframe)
        #     if cv2.waitKey(1) & 0xFF == ord('e'):
        #         # Close = False
        #         break
        #     time.sleep(0.5)
        if Number is None:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                return (max_loc[0], max_loc[1], self.w, self.h)
        # return (Target[0:Number],self.w,self.h)
        # self.outqueue.put(result.download())


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-F', '--folder', type=str,
                        default="/tmp")
    parser.add_argument('-N', '--name', type=str,
                        default="Matchdemo")
    parser.add_argument('-K', '--key', type=str,
                        default="secret password")
    parser.add_argument('-S', '--sample', type=str, default="/home/nvidia/works/uniclass202110/mutiimg/1.png"
                        )
    return parser


# def NoSampleServerApi(address, authkey=b'secret password'):
#     global MAT
#     DOOR = True
#     with Listener(address, authkey=authkey) as listener:
#         while DOOR:
#             print(f"match server  {address} :   is ready!")
#             with listener.accept() as conn:
#                 print(
#                     f"match server  {address} :  {listener.last_accepted} is connecting")
#                 try:
#                     while MAT is None:
#                         conn.send(2)
#                         Msg = conn.recv()
#                         if type(Msg) is np.ndarray and np.max(Msg):
#                             MAT = MatImg(Msg)
#                         elif type(Msg) is int and Msg == 0 or Msg == False or type(Msg) is str and Msg == "0":
#                             # conn.send(0)
#                             print(f"match server : {address}  is closed!")
#                             DOOR = False
#                             break
#                     else:
#                         while True:
#                             conn.send(1)
#                             Msg1 = conn.recv()
#                             if type(Msg1) is tuple:
#                                 ans = tuple([MAT.run(i)
#                                             for i in Msg1 if type(i) is np.ndarray and np.max(i)])
#                                 conn.send(
#                                     tuple([i for i in ans if i]))
#                             elif type(Msg1) is int and Msg1 == 1 :
#                                 MAT = None
#                                 while MAT is None:
#                                     conn.send(2)
#                                     Msg = conn.recv()
#                                     if type(Msg) is np.ndarray and np.max(Msg):
#                                         MAT = MatImg(Msg)
#                                     elif type(Msg) is int and Msg == 0 or Msg == False or type(Msg) is str and Msg == "0":
#                                         # conn.send(0)
#                                         print(f"match server : {address}  is closed!")
#                                         break
#                             else :
#                                 conn.send(-1)
#                                 # elif Msg1 == "00" :
#                                 #     conn.send("closed match class!")
#                                 #     print(
#                                 #         f"match server  {address} :  {listener.last_accepted} is disconnecting")
#                                 #     break
#                                 # elif Msg1 == 0 or Msg1 == False or Msg1 == "0":
#                                 #     print(
#                                 #         f"match server : {address}  is closed!")
#                                 #     DOOR= False
#                                 #     break
#                 except EOFError:
#                     print(
#                         f"match server  {address} :  {listener.last_accepted} will be disconnected")
#                     break
#                 except BrokenPipeError:
#                     print(
#                         f"match server  {address} :  {listener.last_accepted} will be disconnected")
#                 except:
#                     print(
#                         f"[match server  {address}  Global error] :", traceback.format_exc())


def SampleServerApi(address, sample, authkey=b'secret password'):
    Door = True
    with Listener(address, authkey=authkey.encode()) as listener:
        MAT = MatImg(cv2.imread(sample, 0))
        while Door:
            print(f"match server  {address} and Matcher :   is ready!")
            with listener.accept() as conn:
                print(
                    f"match server  {address} :  {listener.last_accepted} is connecting")
                try:
                    while True:
                        conn.send(1)
                        Msg1 = conn.recv()
                        if type(Msg1) is tuple:
                            ans = map(MAT.run, (i for i in Msg1 if type(
                                i) is np.ndarray and np.max(i)))
                            conn.send(
                                tuple([i for i in ans if i]))
                        else:
                            conn.send(-1)
                            # elif Msg1 == "00":
                            #     conn.send("closed match class!")
                            #     print(
                            #         f"match server  {address} :  {listener.last_accepted} will be disconnected")
                            #     break
                            # elif Msg1 == 0 or Msg1 == False or Msg1 == "0":
                            #     print(
                            #         f"match server : {address}  is closed!")
                            #     MAT = None
                            #     break
                except ConnectionResetError:
                    print(
                        f"match server  {address} :  {listener.last_accepted} will be disconnected")
                    break
                except EOFError:
                    print(
                        f"match server  {address} :  {listener.last_accepted} will be disconnected")
                    break
                except BrokenPipeError:
                    print(
                        f"match server  {address} :  {listener.last_accepted} will be disconnected")
                    break
                except:
                    print(
                        f"[match server  {address}   error] :", traceback.format_exc())
                    Door = True
                    break


def main():
    parser = get_parser()
    args = parser.parse_args()
    Folder = args.folder
    Key = args.key
    FileName = f"{Folder}/{args.name}"
    check_filepath(Folder, FileName)
    if args.sample:
        SAMPLE = args.sample
        try:
            SampleServerApi(FileName, SAMPLE, Key)
        except:
            RmFile(FileName)
            print(f"[match server  {FileName}  Global error] :",
                  traceback.format_exc())
        finally:
            RmFile(FileName)
    # else:
    #     try:
    #         NoSampleServerApi(FileName, Key)
    #     except:
    #         RmFile(FileName)
    #         print(f"[match server  {FileName}  Global error] :",
    #               traceback.format_exc())
    #     finally:
    #         RmFile(FileName)

    # with Listener(address, authkey=b'secret password') as listener:
    #     pass

    # def readsample(path):
    #     files = os.listdir(path)
    #     return tuple([f"{path}/{i}" for i in files])
    # HOME = os.getcwd()
    # # 讀檔
    # nowfolder = f"/tmp/image"
    # files = os.listdir(nowfolder)
    # framelist = tuple([cv2.imread(f"{nowfolder}/{i}", 0) for i in files])

    # # 讀sample
    # samplepath = readsample(f"{HOME}/mutiimg")
    # sampleimgs = [cv2.imread(i, 0) for i in samplepath]
    # # samplelen = len((sampleimgs[0],))
    # sampleimgs = tuple([i for i in sampleimgs if np.max(i)])

    # cv2.namedWindow("img", 0)
    # cv2.namedWindow("simg", 0)

    # Close = True

    # for i in sampleimgs:
    #     if Close is False:
    #         break
    #     mat = MatImg(i)
    #     for j in framelist:
    #         starttime = time.time()
    #         ans = mat.run(j)
    #         endtime = time.time()
    #         print(f"runtime: {endtime-starttime}")
    #         if ans and type(ans) is tuple:
    #             x, y, w, h = ans
    #             z = j.copy()
    #             cv2.rectangle(z, (x, y), (x+w, y+h), 255, 2)
    #             cv2.imshow('simg', z)
    #             time.sleep(0.1)
    #         cv2.imshow('img', j)
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             Close = False
    #             break
    #         elif cv2.waitKey(1) & 0xFF == ord('i'):
    #             break
    #         # time.sleep(0.1)
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
