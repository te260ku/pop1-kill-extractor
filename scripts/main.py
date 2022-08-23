from traceback import print_tb
import cv2
import numpy as np
import time
import sys

""" 青 """
lower_inner = np.array([143, 93, 33])
upper_inner = np.array([160, 136, 65])
""" 白 """
lower_border = np.array([0,0,210])
upper_border = np.array([169,21,233])

detection_count = 0
detection_continuation_time = 0
detected = False

count = 0
max_count = 10
fps = 0
tm = cv2.TickMeter()
tm.start()


def nothing(x):
    pass

def proc(img, current_sec=0):
    global detection_count
    global detection_continuation_time
    global detected
    global max_count
    global count
    global fps

    if count == max_count:
        tm.stop()
        fps = max_count / tm.getTimeSec()
        tm.reset()
        tm.start()
        count = 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    result = img.copy()

    # HSV変換
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

    # 値の範囲を指定してマスク生成
    img_mask_raw = cv2.inRange(img_hsv, lower_inner, upper_inner)
    

    #中央値フィルタ
    img_mask = cv2.medianBlur(img_mask_raw, 5)
    

    # edge = cv2.Canny(img_mask, 100, 200)
    # height, width = edge.shape
    # ksize = int(max(height, width) * 0.01)
    # ksize = ksize // 2 * 2 + 1
    # # edge = cv2.dilate(edge, np.ones((ksize, ksize), dtype='uint8'))
    # # edge = cv2.erode(edge, np.ones((ksize, ksize), dtype='uint8'))
    # edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, np.ones((ksize, ksize), dtype='uint8'))
    # contours, _ = cv2.findContours(edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours, _ = cv2.findContours(
    img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    white_area_count = 0

    text = 'rec'

    for cnt in contours:
        area = cv2.contourArea(cnt)
        

        arclen = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, arclen * 0.01, True)
        n_gon = len(approx)
        

        if (n_gon == 4):

            
            
            
            if (area > 30000):
                # 検出した場合
                # print('border area: {}'.format(area))

                cv2.drawContours(result, [approx], -1, (255, 0, 0), 3)
                position = np.asarray(approx).reshape((-1, 2)).max(axis=0).astype('int32')
                px, py = position
                cv2.putText(result, text, (px + 10, py + 10), font, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.putText(result, 'Detected', (10, 130), font, 1.0, (0, 255, 0), 2)

                # x, y, w, h = cv2.boundingRect(cnt)
                # result = cv2.rectangle(result, (x-20, y-10), (x+w+20, y+h+10), (0, 0, 255), 2)

                # rect = cv2.minAreaRect(cnt)
                # box = cv2.boxPoints(rect)
                # box = np.int0(box)
                # result = cv2.drawContours(result, [box], 0, (0, 0, 255), 2)

                # img_bouding = result[y-10:y+h+10, x-20:x+w+20]

                mask = np.zeros_like(img)   # ログの白黒
                cv2.drawContours(mask, [cnt], -1, (255, 255, 255), thickness=-1)

                kernel = np.ones((12,12),np.uint8)
                dilation = cv2.dilate(mask, kernel, iterations=3)   # ログの白黒膨張

                masked = cv2.bitwise_and(img, mask)  # ログのカラー
                masked_2 = cv2.bitwise_and(img, dilation)   # ログのカラー膨張

                masked_3 = cv2.bitwise_xor(masked, masked_2)    # 枠のカラー

                # HSV変換
                img_hsv_2 = cv2.cvtColor(masked_3, cv2.COLOR_BGR2HSV_FULL)
                # 値の範囲を指定してマスク生成
                img_mask_raw_2 = cv2.inRange(img_hsv_2, lower_border, upper_border)
                white_area = cv2.countNonZero(img_mask_raw_2)

                
                # cv2.imshow('image', img_mask_raw_2)
                print(white_area)

                # return
                

                if (400 < white_area < 1000):
                    # 背景によってはインフォーメーションログを誤検出する場合があるので、枠の輪郭抽出→面積・頂点数の判別を入れるといいかもしれない

                    # print('inner area: {}'.format(white_area))

                    if (detected == False):
                        detected = True
                        detection_count += 1
                        # print(current_sec)

                    white_area_count += 1
                    


    if (detected):
        detection_continuation_time += 1
        if (detection_continuation_time > 350):
            detection_continuation_time = 0
            detected = False
    
    cv2.putText(result, 'KILL: ' + str(detection_count), (10, 80), font, 1.0, (0, 255, 0), 2)

    # if (white_area_count == 0):
    #     cv2.imshow('image', result)
    cv2.putText(result, 'FPS: {:.2f}'.format(fps), (10, 30), font, 1.0, (0, 255, 0), thickness=2)
    count += 1
    

    cv2.imshow('image', result)
    
    




def proc_img(img):
    proc(img)
    cv2.waitKey(0)

def proc_video(cap):
    while(cap.isOpened()):
        # フレームを取得
        ret, frame = cap.read()

        if not ret:
            break
        
        current_sec = cap.get(cv2.CAP_PROP_POS_MSEC)
        proc(frame, current_sec=current_sec)
        # qキーが押されたら途中終了
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()


def main():
    img = cv2.imread('../images/test_5.png')
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
    # proc_img(img)

    '''************************************************************
    ** 動画
    ************************************************************'''
    proc_video(cap)

    cv2.destroyAllWindows()

if __name__ == '__main__':
    # args = sys.argv
    # if len(args) == 1:
    #     if type(args[1]) is str:
    #         file_path = args[1]
    #         if file_path.endswith('.png') or file_path.endswith('.jpg'):
    #             pass
    main()