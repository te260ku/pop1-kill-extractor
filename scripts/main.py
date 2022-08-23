import cv2
from cv2 import imshow
import numpy as np


""" 青 """
lower_inner = np.array([143, 93, 33])
upper_inner = np.array([160, 136, 65])
""" 白 """
lower_border = np.array([0,0,210])
upper_border = np.array([169,21,233])

font = cv2.FONT_HERSHEY_SIMPLEX

detection_count = 0
detection_continuation_time = 0
detected = False

frame_count = 0
max_frame_count = 10
fps = 0
tm = cv2.TickMeter()


def nothing(x):
    pass


def proc(img, current_sec=0):
    global detection_count
    global detection_continuation_time
    global detected
    global frame_count
    global max_frame_count
    global fps

    frame_count += 1

    # 動画のfpsを計測
    if frame_count % 10 == 0:
        tm.stop()
        fps = max_frame_count / tm.getTimeSec()
        tm.reset()
        tm.start()

    if (frame_count % 2 == 0):
        return

    result = img.copy()

    '''************************************************************
    ** 画像処理
    ************************************************************'''
    # HSV変換
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
    # マスク画像を生成
    img_mask = cv2.inRange(img_hsv, lower_inner, upper_inner)
    # 中央値フィルタ
    img_median = cv2.medianBlur(img_mask, 5)
    # 輪郭抽出
    contours, _ = cv2.findContours(
    img_median, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        # 輪郭内の領域の面積を計算
        inner_area = cv2.contourArea(cnt)
        # 輪郭を近似して頂点数を計算
        arclen = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, arclen * 0.01, True)
        n_gon = len(approx)
        
        # 輪郭が四角形かつ指定した値よりも大きい面積かどうかを判定
        if (n_gon == 4 and inner_area > 30000):
            # 輪郭とテキストを描画する
            cv2.drawContours(result, [approx], -1, (255, 0, 0), 3)
            position = np.asarray(approx).reshape((-1, 2)).max(axis=0).astype('int32')
            px, py = position
            cv2.putText(result, 'rec', (px + 10, py + 10), font, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

            """ キルログ内部の領域の二値化画像に膨張処理をかけて枠線を含むマスク画像を生成する """
            img_inner_mask = np.zeros_like(img)   # 内部の二値化画像
            cv2.drawContours(img_inner_mask, [cnt], -1, (255, 255, 255), thickness=-1)
            kernel = np.ones((12,12),np.uint8)
            img_dilation = cv2.dilate(img_inner_mask, kernel, iterations=1)   # 内部の二値化膨張画像
            img_inner_color = cv2.bitwise_and(img, img_inner_mask)  # 内部のカラー画像
            img_inner_color_dilation = cv2.bitwise_and(img, img_dilation)   # 内部のカラー膨張画像
            img_border = cv2.bitwise_xor(img_inner_color, img_inner_color_dilation)  # 枠のカラー
            # HSV変換
            img_hsv_border = cv2.cvtColor(img_border, cv2.COLOR_BGR2HSV_FULL)
            # マスク画像を生成
            img_mask_border = cv2.inRange(img_hsv_border, lower_border, upper_border)
            # マスク画像中のキルログの枠線の面積を計算
            white_area = cv2.countNonZero(img_mask_border)

            # 検出された白い枠線の面積が指定した範囲内だった場合、キルログとして判定
            if (400 < white_area < 500):
                # 背景によってはインフォーメーションログを誤検出する場合がある

                cv2.putText(result, 'Detected', (10, 130), font, 1.0, (0, 255, 0), 2)

                # print('inner area: {}'.format(area))
                # print('border area: {}'.format(white_area))

                if (detected == False):
                    detected = True
                    detection_count += 1
                    # print(current_sec)

    """ 検出の重複を防ぐための処理 """
    if (detected):
        detection_continuation_time += 1
        if (detection_continuation_time > 350):  # 指定した時間が経過するまでは、キルログを検出しても無視する
            detection_continuation_time = 0
            detected = False
    
    # 画像中に情報を表示
    cv2.putText(result, 'KILL: ' + str(detection_count), (10, 80), font, 1.0, (0, 255, 0), 2)
    cv2.putText(result, 'FPS: {:.2f}'.format(fps), (10, 30), font, 1.0, (0, 255, 0), thickness=2)

    cv2.imshow('image', result)
    

def proc_img(img):
    proc(img)
    cv2.waitKey(0)


def proc_video(cap):
    tm.start()

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
    img = cv2.imread('../images/test_1.png')
    cap = cv2.VideoCapture('../videos/test_full.mp4')

    # ウィンドウの調整
    if (cap.isOpened()):
        ret, frame = cap.read()
        image_hight, image_width, _ = frame.shape
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 1000, int(1000*image_hight/image_width)) 
        cv2.moveWindow('image', 100, 200)

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