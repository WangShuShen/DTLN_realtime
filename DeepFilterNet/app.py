from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print("Received audio chunk of type:", type(data))
    if isinstance(data, bytes):
        print("Data length in bytes:", len(data))
    emit('audio_response', data)


if __name__ == '__main__':
    socketio.run(app, debug=True)
