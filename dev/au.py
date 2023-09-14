import pydub
import numpy as np
from pydub import AudioSegment
import matplotlib.pyplot as plt



if __name__ == "__main__":

    song = AudioSegment.from_wav("./test/output2.wav")
    song_array = np.array(song.get_array_of_samples())
    song_ch1 = song_array[::2]
    song_ch2 = song_array[1::2]

    wsize = 64

    fig, ax = plt.subplots(1, 1)
    vmax, vmin = 0, 0
    for index in range(song_ch1.shape[0]//wsize):
        data = song_ch1[index*wsize: (index+1)*wsize]
        x = np.arange(index*wsize, (index+1)*wsize)

        vmax = max(vmax, data.max())
        vmin = min(vmin, data.min())

        ax.set_xlim((x.min(), x.max()))
        ax.set_ylim((vmin, vmax))
        if index == 0:
            lines, = ax.plot(x, data)
        else:
            lines.set_data(x, data)
        # リアルタイム描画したい場合
        plt.pause(.05)  
  
        # 保存したい場合
        # plt.savefig("./out/fig_{0:06d}.jpg".format(index))