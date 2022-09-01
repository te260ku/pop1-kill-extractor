import cv2
import numpy as np

def perspective_transform(img, approx, range, color):
    p_original = np.float32(approx)
    min_x = range[0][0]
    min_y = range[1][0]
    w = range[0][1]
    h = range[1][1]
    p_trans = np.float32([[min_x,min_y+h], [min_x+w,min_y+h], [min_x+w,min_y], [min_x,min_y]])
    rows, cols, _ = img.shape
    M = cv2.getPerspectiveTransform(p_original, p_trans)
    img_trans = cv2.warpPerspective(img, M, (cols, rows))
    # HSV変換
    img_hsv_trans = cv2.cvtColor(img_trans, cv2.COLOR_BGR2HSV_FULL)
    # マスク画像を生成
    img_mask_trans = cv2.inRange(img_hsv_trans, color[0], color[1])

    return img_mask_trans