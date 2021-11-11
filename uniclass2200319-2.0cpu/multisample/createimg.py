import cv2
from PIL import Image
import numpy as np
import os
import argparse
import sys
import random
# from numpy.core.fromnumeric import size
from multiprocessing import  Pool 
# import threading
from multiprocessing.connection import Listener
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


HOME = os.getcwd()

cachefile = "/tmp"
cachename = "image"


NowFolder = f"{HOME}/multisample"
Imgfolder = f"{HOME}/multisample/image.yaml"

with open(Imgfolder, 'r') as f:
    Imgpaths = yaml.load(f,Loader=Loader)

# imgpath= "/mnt/98a1b2d9-a271-4ccb-9a8d-ea927725df40/work/uniclass2200319/diffimgsam/newsample.jpg"



Door = True

def get_parser():
    HOME = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument('-P', '--path', type=str,
                        default=f"{HOME}/multisample")
    parser.add_argument('-N', '--name', type=str,
                        default="1")
    parser.add_argument('-I','--image',type=str,
                        default="new_demo/2-0.png")
    parser.add_argument('--debug',type=bool,
                        default=False)
    return parser



def Check_Create(RootPath,Name,DEBUG=None):
    Path = f"{RootPath}/{Name}"
    if DEBUG:
        if os.path.exists(Path):
            return True
        else :
            try:
                os.mkdir(Path)
            except :
                print(sys.exc_info())
                return False
            else:
                return True
    else :
        if not os.path.exists(Path):
            try:
                os.mkdir(Path)
            except :
                return print(sys.exc_info())



def createdata(samplepath,serverportnumber,factor=1):
    # backimg = np.zeros((1920,1080,3), np.uint8)
    backimg = Image.new("RGBA",(960,540),(0,0,0))
    S_img = Image.open(samplepath)
    backimg_w,backimg_h = backimg.size
    S_img_w,S_img_h = S_img.size
    Coordinate = (random.randint(0,960-S_img_w),random.randint(0,540-S_img_h))
    # print(f"W :{S_img_w}, H: {S_img_h}")
    # if coordinate :
    #     if coordinate[0] and backimg_w - coordinate[0] > S_img_w  :
    #         coordinate[0] = backimg_w-S_img_w
    #     if coordinate[1] and  backimg_h - coordinate[1] > S_img_h  :
    #         coordinate[1] = backimg_h-S_img_h
    size_w = int(S_img_w / factor)
    size_h = int(S_img_h / factor)
    if S_img_w > size_w:
        S_img_w = size_w
    if S_img_h > size_h:
        S_img_h = size_h
    icon = S_img.resize((S_img_w,S_img_h),Image.ANTIALIAS)
    # w = int((backimg_w - S_img_w) /2)
    # h= int((backimg_h-S_img_h)/2)
    backimg.paste(icon,Coordinate,mask=None)
    # try :
    #     if coordinate==None or coordinate=="":
    #         coordinate = (w,h)
    #         backimg.paste(icon,coordinate,mask=None)
    #     else:
    #         # print("set xywh!")
    #         backimg.paste(icon,coordinate,mask=None)
    # except:
    #     print("config error")
    #     print(sys.exc_info())
    cvimg = cv2.cvtColor(np.asarray(backimg),cv2.COLOR_RGB2BGR)
    _, img_encode = cv2.imencode('.jpg',cvimg)
    backimg.save(f"{cachefile}/{cachename}/{serverportnumber}.png")
    return  img_encode.tobytes() ,Coordinate
    # backimg.save(f"{folderpath}/screen.png")
    # backimg = backimg.convert("RGBA")
    # img = cv2.imread(samplepath)
    
    
# def Create(num):
#     Coordinate = (random.randint(0,1920),random.randint(0,1080))
#     # Check_Create(NowFolder,num,None)
#     return createdata(imgpath,f"{NowFolder}/{num}",coordinate=Coordinate)

# ImagesData = [ (i[0],i[1]) for i in Imgpaths ]

# Images = tuple([ (x[0],Image.open(x[1])) for x in Imgpaths])


def connecter(num):
    global Imgpaths
    with Listener(("0.0.0.0",num),authkey=b'secret password') as listener:
        numstr = str(num)
        print(f"server ID:{numstr} is ready!")
        while True :
            try:
                imgpath = random.choice(Imgpaths)
                
                imgdata =createdata(imgpath[1],serverportnumber=numstr)
                
                with listener.accept() as conn :
                    conn.send((imgpath[0],*imgdata))
                    Report = conn.recv()
                    if Report and ( Report == 0 or Report == "0" or Report == None or Report == False):
                        print(f"server ID:{num} closed!")
                        break
            except KeyboardInterrupt :
                print(f"server ID:{num} is closed!")
                break
            except:
                print(f"error msg : \n{sys.exc_info()}")
                break
    return False
            
            



def main():
    # global NowFolder
    Check_Create(cachefile,cachename,DEBUG=None)

    # pool = Pool(500)
    # pool_out = pool.map_async(connecter,( x for x in range(11001,11501)))
    # pool.close()
    # pool.join()
    
    for i in range(1,500):
        imgpath = random.choice(Imgpaths)        
        createdata(imgpath[1],serverportnumber=str(i))

    # connecter(12000)
    
    
    # for i in range(11001,11021):
    #     threads.append(threading.Thread(target=connecter,args=(i,)))
        # threads[i].start()
    
    # for i in threads:
    #     i.start()
    # for i in range(11001,11501):
    #     threads[i].start()
    # for i in threads:
    #     i.join()
    # for num in range(12000,12005) :
        # images = createdata(imgpath,f"{NowFolder}/{num}",coordinate=Coordinate)
        # connecter(num)

    # args = get_parser().parse_args()
    # check1 = Check_Create(args.path,args.name)
    # Debug = None
    # if args.debug :
        # Debug = True
    
    # test = tuple([ str(i) for i in range(1,10)])
    
    # PATH = args.path
    # address = ("localhost",12000)
    # with Listener(address,authkey=b'secret password') as listener:
    #     while Door:
    #         try :
    #             print("server is ready!")
    #             with listener.accept() as conn :
    #                 print(f"connecting for {listener.last_accepted}")
    #                 while True:
    #                     try :
    #                         data = tuple(map(Create,tuple( str(i) for i in range(1,10))))
    #                         conn.send(data)
    #                         Report = conn.recv()
    #                         if Report == "Close":
    #                             Door = False
    #                             break
    #                         elif Report == "0" or Report == 0 or Report == None or Report == False:
    #                             print("disconnected !")
    #                             break
    #                         elif Report :
    #                             print(Report)
                            
    #                     except KeyboardInterrupt  :
    #                         Door = False
    #                         break
    #                     except BrokenPipeError:
    #                         print("disconnected or miss !")
    #                         break
    #                     except:
    #                         print("disconnected !")
    #                         print(f"error msg : \n{sys.exc_info()}")
    #                         break
    #         except KeyboardInterrupt :
    #             Door = False
    #         except:
    #             print(f"error msg : \n{sys.exc_info()}")


    # print("server is closed!")
                
    # for i in data :
    #     print(type(i))
    # pool = Pool()
    # pool_out = pool.map_async(Create,(str(i) for i in range(1,501)))
    # pool.close()
    # pool.join()
    
    # [ Create(str(i),PATH,imgpath) for i in range(1,10)]
    
    # PATH1 = args.name
    # for i in range(1,10):
    #     i = str(i)
    #     Coordinate = (random.randint(0,1920),random.randint(0,1080))
    #     if args.debug :
    #         if Check_Create(PATH,i) :
    #             print("folder : ok")
    #         else:
    #             print("folder function  error!")
    #     else :
    #         Check_Create(PATH,i,None)
    #         createdata(imgpath,f"{PATH}/{i}",coordinate=Coordinate)
        
        
        


if __name__ == "__main__":
    main()



