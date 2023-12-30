# 引入所需的庫
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import torch
import numpy as np
from df.enhance import enhance, init_df
import soundfile as sf
import sounddevice as sd

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

REQUIRED_LENGTH = 6500  # 音頻長度
model, df_state, _ = init_df()


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    # 初始化output_buffer
    output_buffer = np.zeros(0, dtype=np.float32)

    # 處理實時音頻數據
    if len(data) % 4 != 0:
        data = data[:-(len(data) % 4)]

    audio_chunk = np.frombuffer(data, dtype=np.float32)
    audio_buffer = np.zeros(REQUIRED_LENGTH, dtype=np.float32)
    audio_buffer = np.concatenate((audio_buffer, audio_chunk))
    if len(audio_buffer) >= REQUIRED_LENGTH:
        audio_to_process = audio_buffer[:REQUIRED_LENGTH]
        audio_buffer = audio_buffer[REQUIRED_LENGTH:]

        audio_input_tensor = torch.from_numpy(audio_to_process).unsqueeze(0)
        enhanced_audio = enhance(model, df_state, audio_input_tensor)
        enhanced_audio_np = enhanced_audio.squeeze().numpy()

        # 把模型inference的結果存到輸出的buffer
        output_buffer = np.concatenate((output_buffer, enhanced_audio_np))

    # 將處理後的數據發送回客戶端
    emit('audio_response', output_buffer.tobytes())


if __name__ == '__main__':
    socketio.run(app, debug=True)
