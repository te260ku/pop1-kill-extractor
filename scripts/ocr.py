import pytesseract
from PIL import Image
import cv2
import numpy as np
import pyperclip
import csv
from moviepy.editor import *
from tqdm import tqdm
import asyncio


# 各種設定
ign = "kkaNbu"
frame_freq = 1.0
kill_time_start_offset = 6
kill_time_end_offset = 3

cap = None
fps = None

preview_thumbnails = []

current_frame = None





# 動画を読み込む
# cap = cv2.VideoCapture("./kanbu_2.mp4")
# # フレームレートを取得
# fps = cap.get(cv2.CAP_PROP_FPS)
# # 総フレーム数を取得
# total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# print(total_frames)


def nothing(x):
    pass

def play_previw_video(video_path):
    cap = cv2.VideoCapture(video_path)


def proc(img_raw):
    height = img_raw.shape[0]
    width = img_raw.shape[1]

    height, width, channels = img_raw.shape[:3]
    img = img_raw[int(height*0.5):int(height*1.0), int(width*0.3):int(width*0.7)]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_min = np.array([90,10,150])
    hsv_max = np.array([120,255,255])

    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    dst1 = cv2.bitwise_and(img, img, mask=mask)
 

    str_img = dst1
    str_data = pytesseract.image_to_string(str_img)
    return str_data


# def proc_str(str_data):
#     result = ign in str_data
#     if result == True:
#         estimated_kill_time = '{{:.{:d}f}}'.format(2).format(current_sec/1000)
#         kill_time.append(estimated_kill_time)
#         print('Estimated Kill Time: {}'.format(estimated_kill_time))
#     return result

def get_preview_thumbnail(sec):
    global cap
    global fps
    frames = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frames)
    ret, frame = cap.read()
    return frame

def proc_new(video_path):
    global cap
    global fps
    # 変数を初期化
    frame_count = 0
    detected_count = 0
    detected_kill_times = []


    cap = cv2.VideoCapture(video_path)
    # フレームレートを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 総フレーム数を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)

    while True:
        try:
            # フレームの読み込み
            ret, frame = cap.read()
            # フレームが読み込めなくなったら終了
            if not ret:
                break

            current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

            # 指定した時間ごとにフレームを抽出
            if frame_count % int(fps*frame_freq) == 0:
                current_time_sec = current_time_ms / 1000
                # print(f"フレーム {frame_count // int(fps)}: 現在の再生時間 {current_time_sec}秒")
                result = proc(frame)
                if (ign in result):
                    # print("detected")
                    minutes, seconds = divmod(current_time_sec, 60)
                    print(f"フレーム {frame_count // int(fps)}: 現在の再生時間 {int(minutes)}分 {seconds:.2f}秒")
                    preview_thumbnails.append(frame)
                    detected_kill_times.append(current_time_sec)
                    detected_count += 1
                    new_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES) + fps * 10)
                    if new_frame_pos <= total_frames:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_pos)
                    
            frame_count += 1
            # progress_value = float('{:.1f}'.format((frame_count/total_frames*100)))
            progress_value = 0.1
            # flet_ocr.set_progress_bar(progress_value)
            

            
        except KeyboardInterrupt:
            break
    cap.release()
    return detected_kill_times


# while True:
#     try:
#         # フレームの読み込み
#         ret, frame = cap.read()
#         # フレームが読み込めなくなったら終了
#         if not ret:
#             break

#         current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

#         # 指定した時間ごとにフレームを抽出
#         if frame_count % int(fps*frame_freq) == 0:
#             current_time_sec = current_time_ms / 1000
#             # print(f"フレーム {frame_count // int(fps)}: 現在の再生時間 {current_time_sec}秒")
#             result = proc(frame)
#             if (ign in result):
#                 # print("detected")
#                 minutes, seconds = divmod(current_time_sec, 60)
#                 print(f"フレーム {frame_count // int(fps)}: 現在の再生時間 {int(minutes)}分 {seconds:.2f}秒")
#                 detected_count += 1
#                 detected = True
#                 new_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES) + fps * 10)
#                 if new_frame_pos <= total_frames:
#                     cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_pos)
                
#         frame_count += 1

#     except KeyboardInterrupt:
#         break

# cap.release()

# print("detected count = " + str(detected_count))