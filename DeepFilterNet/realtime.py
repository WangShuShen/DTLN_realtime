import torch
import sounddevice as sd
import numpy as np
from df.enhance import enhance, init_df

REQUIRED_LENGTH = 6500  # 音頻長度
audio_buffer = np.zeros(REQUIRED_LENGTH, dtype=np.float32)
output_buffer = np.zeros(0, dtype=np.float32)  # 設buffer


def callback(indata, outdata, frames, time, status):
    global audio_buffer, output_buffer

    if status:
        print(status)

    # 把聲音加到buffer
    audio_buffer = np.concatenate((audio_buffer, indata[:, 0]))

    # 檢查buffer是否有足夠長度的聲音
    if len(audio_buffer) >= REQUIRED_LENGTH:
        audio_to_process = audio_buffer[:REQUIRED_LENGTH]
        audio_buffer = audio_buffer[REQUIRED_LENGTH:]

        audio_input_tensor = torch.from_numpy(audio_to_process).unsqueeze(0)
        enhanced_audio = enhance(model, df_state, audio_input_tensor)
        enhanced_audio_np = enhanced_audio.squeeze().numpy()

        # 把模型inference的結果存到輸出的buffer
        output_buffer = np.concatenate((output_buffer, enhanced_audio_np))

    # 檢查聲音長度是否足夠
    if len(output_buffer) >= frames:
        # 取所需長度的音頻輸出
        outdata[:] = output_buffer[:frames].reshape(-1, 1)
        output_buffer = output_buffer[frames:]
    else:
        # 如果輸出的buffer內容長度不足，則塞0，變成沒有聲音
        outdata.fill(0)


if __name__ == "__main__":
    model, df_state, _ = init_df()
    fs = df_state.sr()
    channels = 1

    with sd.Stream(callback=callback, samplerate=fs, channels=channels, dtype='float32'):
        print("降噪中...")
        input("按Enter停止\n")
