import cv2
import numpy as np
from server.server import Server
from server.phash import hash_ans

server = Server()

gpu_img1 = cv2.cuda_GpuMat()
gpu_img = cv2.cuda_GpuMat()

while True:
    conn, addr = server.connect()
    method = cv2.TM_SQDIFF_NORMED
    template = None
    template = server.takeing(conn=conn, TYPE="send_image")
    while template is not False and template is not None:
        w = template.shape[1]
        h = template.shape[0]
        gpu_img1.upload(template)
        gpu_img1 = cv2.cuda.cvtColor(gpu_img1, cv2.COLOR_BGR2GRAY)
        while True:
            frame = server.takeing(conn=conn, TYPE="send_frame")
            if frame is False:
                template = False
                break
            elif frame is not None:
                gpu_img.upload(frame)
                gpu_img = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2GRAY)
                matcher = cv2.cuda.createTemplateMatching(
                    cv2.CV_8UC1, method)
                gresult = matcher.match(gpu_img, gpu_img1)
                res = gresult.download()
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                top_left = min_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                if hash_ans(frame[top_left[1]: top_left[1]+h, top_left[0]:top_left[0]+w], template) < 20:
                    x, y = top_left[0], top_left[1]
                    hero = (str(x)+','+str(y)+','+str(w)+','+str(h))
                    server.takeing(conn=conn, TYPE="report", data=hero)
                else:
                    message = server.takeing(
                        conn=conn, TYPE="report", data="None")
