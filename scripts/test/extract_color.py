import cv2
import numpy as np

img = cv2.imread('../images/test.png')

# HSV変換
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

# 値の範囲を指定してマスク生成
lower = np.array([143, 93, 33])
upper = np.array([158, 136, 65])
img_mask = cv2.inRange(img_hsv, lower, upper)

# イメージの表示
cv2.imshow('image', img_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()