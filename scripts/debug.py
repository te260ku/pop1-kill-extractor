import cv2
import main

def display():
    img = cv2.imread('../images/test_1.png')
    cap = cv2.VideoCapture('../videos/test_short_1.mp4')

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
    # main.proc_img(img)

    '''************************************************************
    ** 動画
    ************************************************************'''
    main.proc_video(cap)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    display()