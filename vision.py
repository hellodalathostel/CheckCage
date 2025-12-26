import cv2
import numpy as np
import os

ORB = cv2.ORB_create()
SAMPLES = []

for file in os.listdir("sample_images"):
    img = cv2.imread(f"sample_images/{file}", 0)
    kp, des = ORB.detectAndCompute(img, None)
    SAMPLES.append(des)

def similarity_score(img_bytes):
    img_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    kp, des = ORB.detectAndCompute(img, None)

    if des is None:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    scores = []

    for sample in SAMPLES:
        matches = bf.match(des, sample)
        scores.append(len(matches))

    return max(scores) / 100
