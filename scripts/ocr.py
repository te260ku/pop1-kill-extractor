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






def nothing(x):
    pass

def play_previw_video(video_path):
    cap = cv2.VideoCapture(video_path)

def frames_to_seconds(frame_count, fps):
    seconds = frame_count / fps
    return seconds



def get_ocr_result(img_raw):
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


def get_preview_thumbnail(sec):
    global cap
    global fps
    frames = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frames)
    ret, frame = cap.read()
    return frame

def proc(video_path=None, ign=None):
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

            # 指定した時間ごとにフレームを抽出
            if frame_count % int(fps*frame_freq) == 0:
                current_time_sec = current_time_ms / 1000
                # print(f"フレーム {frame_count // int(fps)}: 現在の再生時間 {current_time_sec}秒")
                result = get_ocr_result(frame)
                if (ign in result):
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

        except KeyboardInterrupt:
            break
    cap.release()
    finished = True
    progress_value = 1.0
    return detected_kill_times




def cut_video(input_file, output_video_path, segments, separated):

    clips = []

    # 動画を切り出す
    for segment in segments:
        start_time = segment[0]
        end_time = segment[1]
        clip = VideoFileClip(input_file).subclip(start_time, end_time)
        clips.append(clip)

    print(clips)


    if (separated == False):
        # 結合の場合
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
        # 個別の場合
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




def calc_segments(kill_times, total_time):

    def trim_within_total_time(t):
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
    print("動画を切り出しています")

    '''
    動画の合計時間を計算
    '''
    cap = cv2.VideoCapture(input_video_file)
    # フレームレートを取得
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 総フレーム数を取得
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = frames_to_seconds(total_frames, fps)
    cap.release()


    # クリップにする動画の区間のリストを取得
    segments = calc_segments(kill_times, total_time)
    print(segments)

    # 動画を書き出す
    cut_video(input_video_file, output_video_path, segments, separated)

