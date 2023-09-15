import librosa
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
from os.path import dirname
import scipy.signal
from scipy import fftpack

input_video_file = '../videos/sample_2_trim.wav'
kill_audio_file = '../audio/kill_audio_1.wav'
# kill_audio_file = './audio/kill_audio_2.wav'
trimmed_sorted_peak_times = []
concat_detect_create_video_checkbox_changed = True
processing_status_text = ""


import librosa
import numpy as np

def fft_ave(data, Fs):
    fft = np.fft.fft(data)                      # FFT（実部と虚部）
    fft_amp = np.abs(fft / (Fs / 2))            # 振幅成分を計算
    return fft_amp


def calc_fft_mean_in_window(target_sound_file, game_audio_file, min_freq, max_freq, segment):
    # 効果音の読み込み
    target_sound, sr_target = librosa.load(target_sound_file, sr=None)
    
    # ゲーム音声の読み込み
    game_audio, sr_game = librosa.load(game_audio_file, sr=None)

    game_audio = game_audio[segment[0]:segment[1]]
    # game_audio = game_audio[565136:829735]

    
    # 効果音の長さを取得
    target_sound_length = len(target_sound)
    
    # 窓のサイズを効果音と同じに設定
    window_size = target_sound_length
    
    # 窓をスライドさせるステップサイズ
    step_size = 512
    
    # 平均値を保存するリスト
    mean_values = []
    std_values = []
    
    # ゲーム音声を窓で切り出して平均値を計算
    for i in range(0, len(game_audio) - window_size + 1, step_size):
        windowed_audio = game_audio[i:i + window_size]
        
        # ウィンドウ内の平均を計算
        fft_result = fft_ave(windowed_audio, sr_game)
        frequencies = np.fft.fftfreq(len(fft_result), 1.0 / sr_game)
        min_bin = np.argmin(np.abs(frequencies - min_freq))
        max_bin = np.argmin(np.abs(frequencies - max_freq))
        
        # 指定した周波数帯域内の振幅を取得
        extracted = fft_result[min_bin:max_bin]
        
        # 指定した周波数帯域内の平均値を計算
        mean_value = np.mean(extracted)
        mean_values.append(mean_value)

        std_value = np.std(extracted)
        std_values.append(std_value)
    
    return mean_values, std_values






def cut_video(input_file, output_file, segments):
    clips = []
    # enumerate(tqdm(segments, desc='Processing', unit='segment')):
    for segment in segments:
        start_time = segment[0]
        end_time = segment[1]
        clip = VideoFileClip(input_file).subclip(start_time, end_time)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_file, audio_codec='aac')




def extract_kill_audio_time(input_video_file):

    print("動画ファイルを読み込んでいます")
    # ターゲット効果音の読み込み
    target_sound, sr_target = librosa.load(kill_audio_file, sr=None)
    # ゲーム音声の読み込み
    game_audio, sr_game = librosa.load(input_video_file, sr=None)

    print(len(game_audio))


    print("効果音を検索しています")
    # クロスコレレーションを計算して、効果音の再生位置を見つける
    # cross_correlations = np.correlate(game_audio, target_sound, mode='full')
    cross_correlations = np.correlate(game_audio, target_sound, mode='full')
    # クロスコレレーションのピークを検出
    peak_indices = np.argsort(cross_correlations)[-100:]
    peak_times = peak_indices / sr_game
    sorted_peak_times = np.sort(peak_times)
    
    # 差が0.5未満の場合、一番小さい値で置き換える
    threshold = 1
    i = 0
    while i < len(sorted_peak_times):
        trimmed_sorted_peak_times.append(sorted_peak_times[i])
        j = i + 1
        while j < len(sorted_peak_times) and sorted_peak_times[j] - sorted_peak_times[i] < threshold:
            j += 1
        i = j

    












    if len(peak_indices) > 0:
        print("効果音が以下の時間に再生されました：")
        i = 0
        for peak_time in trimmed_sorted_peak_times:
            minutes = int(peak_time // 60)
            seconds = int(peak_time % 60)
            # cross_correlation = cross_correlations[peak_indices[i]]
            



            
            min_freq = 32
            max_freq = 64

            # 平均値を計算
            segment = (int((peak_time-2)*sr_game), int((peak_time+2)*sr_game))
            mean_values, std_values = calc_fft_mean_in_window(kill_audio_file, input_video_file, min_freq, max_freq, segment)

            threshold_mean = 0.02
            threshold_std = 0.02

            for i, (mean_value, std_value) in enumerate(zip(mean_values, std_values)):
                if mean_value >= threshold_mean and std_value <= threshold_std:
                    print(f"time:{minutes}:{seconds} / frame:{segment[0]} - {segment[1]} / mean:{mean_value} / std:{std_value}")
                    break



            i += 1
    else:
        print("効果音が見つかりませんでした")



def create_video(input_video_file):
    print("動画を切り出しています")
    segments = []
    for peak_time in trimmed_sorted_peak_times:
        segments.append((int(peak_time-3), int(peak_time+3)))
    output_video_file = os.path.join(dirname(input_video_file), 'output.mp4')
    cut_video(input_video_file, output_video_file, segments)


extract_kill_audio_time(input_video_file)
