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
# 48000

frame_length = 2048
hop_length = frame_length // 4
pre_max = 0.1 * sr_game // hop_length
post_max = 0.1 * sr_game // hop_length
pre_avg = 0.1 * sr_game // hop_length
post_avg = 0.1 * sr_game // hop_length
wait = 5 * sr_game // hop_length
delta = 0.1

# クロスコレレーションを計算して、効果音の再生位置を見つける
cross_correlation = np.correlate(game_audio, target_sound, mode='full')


# クロスコレレーションのピークを検出
# peak_indices = librosa.util.peak_pick(cross_correlation, pre_max=pre_max, post_max=post_max, pre_avg=pre_avg, post_avg=post_avg, delta=delta, wait=wait)
# peak_indices = librosa.util.peak_pick(cross_correlation, pre_max=3, post_max=3, pre_avg=3, post_avg=3, delta=0.1, wait=10)
# peak_indices = librosa.util.peak_pick(cross_correlation, pre_max=5, post_max=5, pre_avg=5, post_avg=5, delta=0.5, wait=48000*5)
# peak_indices = np.where(cross_correlation == np.max(cross_correlation))[0]


peak_indices = np.argsort(cross_correlation)[-5:]
peak_times = peak_indices / sr_game

sorted_peak_times = np.sort(peak_times)

print(sorted_peak_times)

# 隣接する値同士の差を計算
differences = np.diff(sorted_peak_times)

print(differences)

result_array = []

# 差が0.5未満の場合、一番小さい値で置き換える
threshold = 1
i = 0
while i < len(sorted_peak_times):
    result_array.append(sorted_peak_times[i])
    j = i + 1
    while j < len(sorted_peak_times) and sorted_peak_times[j] - sorted_peak_times[i] < threshold:
        j += 1
    i = j


print(result_array)

if len(peak_indices) > 0:
    print("効果音が以下の時間に再生されました：")
    
    # 2秒以内に複数回検出された場合、1回とみなすための変数を初期化
    last_detected_time = None
    
    i = 0
    for peak_time in result_array:
        # 各ピークの再生時間を計算
        # peak_time = peak_index / sr_game

        minutes = int(peak_time // 60)
        seconds = int(peak_time % 60)
        print(f"{minutes}分 {seconds}秒, {cross_correlation[peak_indices[i]]}")

        # 740.9059
        # 772.5155

        i += 1
        
        # # 前回の検出から2秒以上経過した場合、新たな検出として扱う
        # if last_detected_time is None or (play_time_seconds - last_detected_time) >= 0.5:
        #     # 分と秒に変換して表示
        #     minutes = int(play_time_seconds // 60)
        #     seconds = int(play_time_seconds % 60)
        #     print(f"{minutes}分 {seconds}秒")
        
        # 最後に検出された時間を更新
        # last_detected_time = peak_time
else:
    print("効果音が見つかりませんでした。")







