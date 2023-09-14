import librosa
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips


# input_video_file = '../videos/sample_1_trim.mp4'
output_video_file = '../videos/output.mp4'
kill_audio_file = './audio/kill_audio_1.wav'
trimmed_sorted_peak_times = []
concat_detect_create_video_checkbox_changed = True


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


    print("効果音を探索しています")
    # クロスコレレーションを計算して、効果音の再生位置を見つける
    cross_correlations = np.correlate(game_audio, target_sound, mode='full')
    # クロスコレレーションのピークを検出
    peak_indices = np.argsort(cross_correlations)[-5:]
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
            cross_correlation = cross_correlations[peak_indices[i]]
            print(f"{minutes}分 {seconds}秒 cross_correlation: {cross_correlation}")
            i += 1
    else:
        print("効果音が見つかりませんでした")

    create_video(input_video_file)


def create_video(input_video_file):
    print("動画を切り出しています")
    segments = []
    for peak_time in trimmed_sorted_peak_times:
        segments.append((int(peak_time-3), int(peak_time+3)))
    cut_video(input_video_file, output_video_file, segments)