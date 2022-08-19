from tracemalloc import start
import cv2
import numpy as np
import time
import sys

def nothing(x):
    pass

def proc(img, *current_sec):
    global detection_count
    global detection_continuation_time
    global detected

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

    font = cv2.FONT_HERSHEY_PLAIN

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if (area > 20000):
            # 検出した場合
            arclen = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, arclen * 0.01, True)
            
            n_gon = len(approx)
            if n_gon == 4:
                text = 'rectangle'
                cv2.drawContours(result, [approx], -1, (255, 0, 0), 3)
                position = np.asarray(approx).reshape((-1, 2)).max(axis=0).astype('int32')
                px, py = position
                cv2.putText(result, text, (px + 10, py + 10), font, 2.0, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.putText(result, 'Detected', (40, 200), font, 4.0, (255, 255, 255), 2, cv2.LINE_AA)
                if (detected == False):
                    detected = True
                    detection_count += 1
                    # print(current_sec)
            else:
                continue

    if (detected):
        detection_continuation_time += 1
        if (detection_continuation_time > 100):
            detection_continuation_time = 0
            detected = False
    
    cv2.putText(result, 'KILL: ' + str(detection_count), (40, 100), font, 4.0, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('image', result)


lower = np.array([143, 93, 33])
upper = np.array([160, 136, 65])
detection_count = 0
detection_continuation_time = 0
detected = False

def proc_img(img):
    proc(img)
    cv2.waitKey(0)

def proc_video(cap):
    while(cap.isOpened()):
        # フレームを取得
        ret, frame = cap.read()
        
        current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)
        proc(frame, current_sec=current_sec)
        # time.sleep(0.05)
        # qキーが押されたら途中終了
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()


def main():
    img = cv2.imread('../images/test_1.png')
    cap = cv2.VideoCapture('../videos/test_full.mp4')

    # ウィンドウの調整
    image_hight, image_width, image_color = img.shape
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', 1000, int(1000*image_hight/image_width)) 
    cv2.moveWindow('image', 100, 200)

    area_range_x = [int(image_width/4)-100, int((image_width/4)*3)+100]
    area_range_y = [int(image_hight/4), int(image_hight)]
    area_range = [area_range_x, area_range_y]

    '''************************************************************
    ** 画像
    ************************************************************'''
    proc_img(img)

    '''************************************************************
    ** 動画
    ************************************************************'''
    # proc_video(cap)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    # args = sys.argv
    # if len(args) == 1:
    #     if type(args[1]) is str:
    #         file_path = args[1]
    #         if file_path.endswith('.png') or file_path.endswith('.jpg'):
    #             pass
    main()