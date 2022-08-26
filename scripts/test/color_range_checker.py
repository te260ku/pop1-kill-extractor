import cv2
import numpy as np

# 無処理
def nothing(x):
    pass

# ウィンドウの生成
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# トラックバーの生成

cv2.createTrackbar('minH', 'image', 0, 255, nothing)
cv2.createTrackbar('maxH', 'image', 255, 255, nothing)
cv2.createTrackbar('minS', 'image', 0, 255, nothing)
cv2.createTrackbar('maxS', 'image', 255, 255, nothing)
cv2.createTrackbar('minV', 'image', 0, 255, nothing)
cv2.createTrackbar('maxV', 'image', 255, 255, nothing)

# イメージの読み込み
img = cv2.imread('../images/test.png')

# HSV変換
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

while True:
    # トラックバーの値の取得
    minH = cv2.getTrackbarPos('minH', 'image')
    minS = cv2.getTrackbarPos('minS', 'image')
    minV = cv2.getTrackbarPos('minV', 'image')
    maxH = cv2.getTrackbarPos('maxH', 'image')
    maxS = cv2.getTrackbarPos('maxS', 'image')
    maxV = cv2.getTrackbarPos('maxV', 'image')

    # 画像の更新
    img_mask = cv2.inRange(img_hsv, np.array([minH, minS, minV]), np.array([maxH, maxS, maxV]))
    cv2.imshow('image', img_mask)

    # qキーで終了
    if cv2.waitKey(16) & 0xFF == ord('q'):
        break

# 破棄
cv2.destroyAllWindows()