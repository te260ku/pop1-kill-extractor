import librosa
import numpy as np


# ターゲット効果音のファイル名
target_sound_file = "../audio/kill_audio_1.wav"
# ターゲット効果音の読み込み
target_sound, sr_target = librosa.load(target_sound_file, sr=None)
# ゲーム音声のファイル名
game_audio_file = "../videos/sample_1.mp4"
# ゲーム音声の読み込み
game_audio, sr_game = librosa.load(game_audio_file, sr=None)


# クロスコレレーションを計算して、効果音の再生位置を見つける
cross_correlations = np.correlate(game_audio, target_sound, mode='full')
# クロスコレレーションのピークを検出
peak_indices = np.argsort(cross_correlations)[-5:]
peak_times = peak_indices / sr_game
sorted_peak_times = np.sort(peak_times)
trimmed_sorted_peak_times = []
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