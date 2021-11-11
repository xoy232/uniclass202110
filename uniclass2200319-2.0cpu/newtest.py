import cv2
import numpy as np
# from server.server import Server
from server.phash import hash_ans
import os
import time 

HOME = os.getcwd()

# server = Server()

gpu_img1 = cv2.cuda_GpuMat()
gpu_img2 = cv2.cuda_GpuMat()
gpu_img3 = cv2.cuda_GpuMat()
gpu_img = cv2.cuda_GpuMat()
gpu_img4 = cv2.cuda_GpuMat()


template1 = cv2.imread(f"{HOME}/new_demo/1.png")
template2 = cv2.imread(f"{HOME}/diffimgsam/newsample7682.jpg")
template3 = cv2.imread(f"{HOME}/diffimgsam/newsample7681.jpg")

# template1 = cv2.cvtColor(template1,cv2.COLOR_BGR2GRAY)
# template2 = cv2.cvtColor(template2,cv2.COLOR_BGR2GRAY)
# template3 = cv2.cvtColor(template3,cv2.COLOR_BGR2GRAY)

w1 = template1.shape[1]
h1 = template1.shape[0]
w2 = template2.shape[1]
h2 = template2.shape[0]
w3 = template3.shape[1]
h3 = template3.shape[0]

gpu_img1.upload(template1)
gpu_img2.upload(template2)
gpu_img3.upload(template3)


# gpu_img1 = cv2.cuda.cvtColor(gpu_img1, cv2.COLOR_BGR2GRAY)
# gpu_img2 = cv2.cuda.cvtColor(gpu_img2, cv2.COLOR_BGR2GRAY)
# gpu_img3 = cv2.cuda.cvtColor(gpu_img3, cv2.COLOR_BGR2GRAY)



method = cv2.TM_SQDIFF_NORMED
matcher = cv2.cuda.createTemplateMatching(
    cv2.CV_8UC1, method)

def Matimg(gpuframe,gpusampleimg,sampleimg,realsampleimg,w,h):
    # global matcher
    gresult = matcher.match(gpuframe, gpusampleimg)
    res = gresult.download()
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    # bottom_right = (top_left[0] + w, top_left[1] + h)
    roiimg = sampleimg[top_left[1]:top_left[1]+h,top_left[0]:top_left[0]+w]
    gpu_img4.upload(roiimg)
    # roiimg = cv2.cvtColor(roiimg, cv2.COLOR_BGR2GRAY)
    # res = cv2.matchTemplate(roiimg,template2,method)
    gresult1 = matcher.match(gpu_img4, gpu_img2)
    res1 = gresult1.download()
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    
    resimg = roiimg[min_loc1[1]:min_loc1[1]+h2,min_loc1[0]:min_loc1[0]+w2]

    # if hash_ans(frame[top_left[1]: top_left[1]+h, top_left[0]:top_left[0]+w], sampleimg) <= 20:
        # x, y = top_left[0], top_left[1]
    # hero = (str(x)+','+str(y)+','+str(w)+','+str(h))
    # cv2.imshow('img1',resimg)
    # cv2.imshow('img2',template2)
    if hash_ans(resimg, template2) < 25:
        return (top_left[0],top_left[1],top_left[0] + w, top_left[1] + h)
    elif hash_ans(sampleimg[top_left[1]: top_left[1]+h, top_left[0]:top_left[0]+w], realsampleimg) < 25:
        return (top_left[0],top_left[1],top_left[0] + w, top_left[1] + h)

cv2.namedWindow("img",0)

while True:
    cap = cv2.VideoCapture("http://169.254.7.129/capture.jpg")
    _,frame = cap.read()
    cap.release()
    # frame = cv2.imread("http://169.254.7.129/capture.jpg")
    if not np.max(frame):
        continue
    gpu_img.upload(frame)
    # gpu_img = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2GRAY)
    
    gresult = matcher.match(gpu_img, gpu_img3)
    res = gresult.download()
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = min_loc
    roi_img = frame[top_left[1]: top_left[1]+h3, top_left[0]:top_left[0]+w3]
    if hash_ans(roi_img, template3) <= 20:
        cv2.rectangle(frame, (top_left[0], top_left[1]), (top_left[0]+w3, top_left[1]+h3), (0, 0,255), 5)
    elif np.max(roi_img) :
        gpu_img4.upload(roi_img)
        gresult1 = matcher.match(gpu_img4, gpu_img2)
        res1 = gresult1.download()
        min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
        resimg = roi_img[min_loc1[1]:min_loc1[1]+h2,min_loc1[0]:min_loc1[0]+w2]
        if hash_ans(resimg, template2) <= 20 :
            cv2.rectangle(frame, (top_left[0], top_left[1]), (top_left[0]+w3, top_left[1]+h3), (0, 0,255), 5)

    


    
    # img3roi = Matimg(gpuframe=gpu_img,gpusampleimg=gpu_img1,sampleimg=template1,w=w1,h=h1)
    # img2roi = Matimg(gpuframe=gpu_img,gpusampleimg=gpu_img2,sampleimg=template2,w=w2,h=h2)
    # img1roi = Matimg(gpuframe=gpu_img,gpusampleimg=gpu_img3,sampleimg=frame,realsampleimg=template3,w=w3,h=h3)





    # print("img1 :",img1roi)
    # print("img2 :",img2roi)
    # print("img3 :",img3roi)
    # [cv2.rectangle(frame, (x[0], x[1]), (x[2], x[3]), (0, 0,255), 5) for x in (img1roi,img2roi,img3roi) if x and len(x) == 4]
    # if img1roi and len(img1roi) == 4 :
    #     cv2.rectangle(frame, (img1roi[0], img1roi[1]), (img1roi[2], img1roi[3]), (0, 0,255), 5)
    cv2.imshow("img",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)
    # time.sleep(10)

cv2.destroyAllWindows()
    # gresult = matcher.match(gpu_img, gpu_img1)
    # res = gresult.download()
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # top_left = min_loc
    # bottom_right = (top_left[0] + w1, top_left[1] + h1)
    # if hash_ans(frame[top_left[1]: top_left[1]+h1, top_left[0]:top_left[0]+w1], template1) < 20:
    #     x, y = top_left[0], top_left[1]
    #     hero = (str(x)+','+str(y)+','+str(w1)+','+str(h1))
    #     print(hero)
    
