import cv2

hashFun = cv2.img_hash.PHash_create()


# def phash(img):
#     hashFun.create()
#     return hashFun.compute(img)


# def Hamming_check(hashA, hashB):
#     return hashFun.compare(hashA, hashB)


def hash_ans(img1, img2):
    hashA = hashFun.compute(img1)
    hashB = hashFun.compute(img2)
    return hashFun.compare(hashA, hashB)
    # print(ans)
    # return ans
