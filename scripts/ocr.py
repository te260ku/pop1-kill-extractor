import pytesseract
from PIL import Image
import cv2
import numpy as np
import pyperclip
import csv
from moviepy.editor import *
from tqdm import tqdm
import asyncio
import flet_ocr
from os.path import dirname


# 各種設定
ign = None
frame_freq = 1.0
kill_time_start_offset = 6
kill_time_end_offset = 3

cap = None
fps = None

preview_thumbnails = []

# current_frame = None
detected_kill_times = []
detected_kill_frames = []

finished = False
progress_value = 0

total_time = None




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

def frames_to_seconds(frame_count, fps):
    seconds = frame_count / fps
    return seconds



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

def proc_new(video_path=None, ign=None):
    global cap
    global fps
    global detected_kill_frames
    global detected_kill_times
    global finished
    global progress_value
    global total_time
    # 変数を初期化
    frame_count = 0
    detected_count = 0
    detected_kill_times = []


    cap = cv2.VideoCapture(video_path)
    # フレームレートを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 総フレーム数を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = frames_to_seconds(total_frames, fps)
    
    print(total_frames)

    while True:
        try:
            if finished == True:
                break
            # フレームの読み込み
            ret, frame = cap.read()
            # フレームが読み込めなくなったら終了
            if not ret:
                break

            current_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

            progress_value = round(current_frame/total_frames, 3)
            # print(progress_value)
            # print(current_frame)

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

                    rounded_time_sec = round(current_time_sec, 2)
                    detected_kill_times.append(rounded_time_sec)
                    detected_kill_frames.append(current_frame)
                    detected_count += 1
                    new_frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES) + fps * 10)
                    if new_frame_pos <= total_frames:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame_pos)
                    
            
            frame_count += 1
            
            # print(progress_value)
            # progress_value = 0.1
            
            # flet_ocr.set_progress_bar_value(progress_value)

            
        except KeyboardInterrupt:
            break
    cap.release()
    finished = True
    progress_value = 1.0
    return detected_kill_times




def cut_video(input_file, output_video_path, segments, separated):
    
    clips = []
    # enumerate(tqdm(segments, desc='Processing', unit='segment')):
    for segment in segments:
        start_time = segment[0]
        end_time = segment[1]
        clip = VideoFileClip(input_file).subclip(start_time, end_time)
        clips.append(clip)

    print(clips)

    if (separated == False):
        output_file = os.path.join(output_video_path, 'output_newnew.mp4')
        final_clip = concatenate_videoclips(clips)
        # final_clip.write_videofile(output_file)
        # final_clip.write_videofile(output_file, audio_codec='aac')
        final_clip.write_videofile(
            output_file,  
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True
        )
    else:
        count = 0
        for clip in clips:
            file_name = "new" + "_" + str(count) + ".mp4"
            output_file = os.path.join(output_video_path, file_name)
            
            print(output_file)
            clip.write_videofile(
                output_file,  
                codec='libx264', 
                audio_codec='aac', 
                temp_audiofile='temp-audio.m4a', 
                remove_temp=True
            )
            count += 1




def calc_segments(kill_times):

    def trim_within_total_time(t):
        global total_time
        result = t
        if t < 0:
            result = 0
        elif t > total_time:
            result = int(total_time)
        return result


    segments = []
    # tm = [4, 17]
    tm = kill_times
    for peak_time in tm:
        start_time = trim_within_total_time(int(peak_time-3))
        end_time = trim_within_total_time(int(peak_time+3))
        
        segments.append((start_time, end_time))
    return segments


def create_video(input_video_file, output_video_path, separated, kill_times):
    global total_time


    print("動画を切り出しています")


    cap = cv2.VideoCapture(input_video_file)
    # フレームレートを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 総フレーム数を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = frames_to_seconds(total_frames, fps)
    cap.release()


    seg = calc_segments(kill_times)

    print(seg)
    
    
    cut_video(input_video_file, output_video_path, seg, separated)


    
    # try:
    #     cut_video(input_video_file, output_video_file, segments)
    #     return True
    # except:
    #     return False


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