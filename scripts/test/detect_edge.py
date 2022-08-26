import cv2
import numpy as np
import time

def nothing(x):
    pass

def proc(img):
    # HSV変換
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

    # 値の範囲を指定してマスク生成
    img_mask_raw = cv2.inRange(img_hsv, lower, upper)

    #中央値フィルタ
    img_mask = cv2.medianBlur(img_mask_raw, 15)

    edge = cv2.Canny(img_mask, 100, 200)
    height, width = edge.shape
    ksize = int(max(height, width) * 0.01)
    ksize = ksize // 2 * 2 + 1
    #edge = cv2.dilate(edge, np.ones((ksize, ksize), dtype='uint8'))
    #edge = cv2.erode(edge, np.ones((ksize, ksize), dtype='uint8'))
    edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, np.ones((ksize, ksize), dtype='uint8'))

    contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    result = img.copy()
    # cv2.drawContours(result, contours, -1, (255, 0, 0), 3, cv2.LINE_AA)

    font = cv2.FONT_HERSHEY_SIMPLEX

    for cnt in contours:
        arclen = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, arclen * 1.0e-2, True)
        
        n_gon = len(approx)
        # text = 'unknown'
        text = ''
        if n_gon > 10:
            # text = 'circle'
            text = ''
            continue
        elif n_gon == 6:
            text = 'hexagon'
        elif n_gon == 5:
            text = 'pentagon'
        elif n_gon == 4:
            text = 'rectangle'
        elif n_gon == 3:
            text = 'triangle'
        else:
            continue

        cv2.drawContours(result, [approx], -1, (255, 0, 0), 3)
        
        position = np.asarray(approx).reshape((-1, 2)).max(axis=0).astype('int32')
        px, py = position
        cv2.putText(result, text, (px + 10, py + 10), font, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('image', result)


lower = np.array([143, 93, 33])
upper = np.array([160, 136, 65])

def main():
    img = cv2.imread('../images/test_1.png')

    # ウィンドウの調整
    image_hight, image_width, image_color = img.shape
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1000, int(1000*image_hight/image_width)) 
    cv2.moveWindow('image', 100, 200)

    '''************************************************************
    ** 画像
    ************************************************************'''
    # proc(img)
    # cv2.waitKey(0)

    '''************************************************************
    ** 動画
    ************************************************************'''
    cap = cv2.VideoCapture('../videos/test.mp4')
    while(cap.isOpened()):
        # フレームを取得
        ret, frame = cap.read()
        proc(frame)
        time.sleep(0.05)
        # qキーが押されたら途中終了
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()