import numpy as np 
import cv2

imgCrop = None

while True:
    cap = cv2.VideoCapture("http://169.254.7.129/capture.jpg")
    _,frame = cap.read()
    cap.release()
    if not np.max(frame):
        continue
    cv2.namedWindow("img",0)
    cv2.imshow("img",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif  cv2.waitKey(1) & 0xFF == ord('b'):
        rect = cv2.selectROI("img",frame,True,False)
        if rect and len(rect) == 4 :
            (x,y,w,h) = rect
            imgCrop=frame[y:y+h,x:x+w]
            if imgCrop is not None and  type(imgCrop) is np.ndarray and np.max(imgCrop) :
                # cv2.namedWindow("roi",0)
                # cv2.imshow("roi",imgCrop)
                try :
                    cv2.imwrite("newsample768.jpg",imgCrop)
                except:
                    pass
                else :
                    print("ok")
                    break

cv2.destroyAllWindows()

