import cv2
from imutils.video import WebcamVideoStream
import subprocess
import os
from client import Clientmanger
import time

HOME = os.getcwd()
# p =subprocess.Popen("python3 "+HOME+"/sockets/user/sender.py",shell=True)
cap = WebcamVideoStream(src="http://192.168.50.30:10000/?action=stream")
cap.start()
time.sleep(3)

client = Clientmanger(HOST='192.168.55.1', PORT=9000)
img = cv2.imread(HOME+"/demo_img/2.png")
check = client.send_msg(img, TYPE="send_image")

while check is True:
    frame = cap.read()
    data = client.send_msg(frame, TYPE="send_frame")
    if data:
        x, y, w, h = data
        top_left = (int(x), int(y))
        bottom_right = (top_left[0]+int(w), top_left[1]+int(h))
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)
    elif data is False:
        break
    else:
        print(data)
        continue
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0XFF == ord('q'):
        break


cap.stop()
time.sleep(1)
cap.stream.release()
# p.kill()
cv2.destroyAllWindows()
