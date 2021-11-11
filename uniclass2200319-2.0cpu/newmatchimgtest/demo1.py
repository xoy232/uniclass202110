import cv2
from matplotlib import pyplot as plt

def match_ORB():
	img1 = cv2.imread('/mnt/98a1b2d9-a271-4ccb-9a8d-ea927725df40/work/uniclass2200319/new_demo/2-0.png',0)
	img2 = cv2.imread('/mnt/98a1b2d9-a271-4ccb-9a8d-ea927725df40/work/uniclass2200319/new_demo/2.png',0)

	# 使用ORB特徵檢測器和描述符，計算關鍵點和描述符
	orb = cv2.ORB_create()
	kp1, des1 = orb.detectAndCompute(img1,None)
	kp2, des2 = orb.detectAndCompute(img2,None)

	bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING, crossCheck=True)
	matches = bf.match(des1,des2)
	matches = sorted(matches, key = lambda x:x.distance)

	img3 = cv2.drawMatches(img1=img1,keypoints1=kp1,
						   img2=img2,keypoints2=kp2,
						   matches1to2=matches,
						   outImg=img2, flags=2)
	return img3

if __name__ == '__main__':
    img3 = match_ORB()
    plt.imshow(img3)
    plt.show()