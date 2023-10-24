import tkinter as tk
import pyaudio
import wave
import threading
import os
import soundfile as sf
import time
import shutil


class Recorder:
    def __init__(self, chunk=6000, channels=1, rate=48000):
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.recording = False
        self.playing = False
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  output=True,
                                  input_device_index=23,
                                  output_device_index=27,
                                  frames_per_buffer=self.chunk)

    def start_recording(self):
        self.recording = True
        self.playing = True
        threading.Thread(target=self.__record_and_play).start()

    def __record_and_play(self):
        self.frames = []
        while self.recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)
            if self.playing:
                self.stream.write(data)

    def stop_recording(self):
        self.recording = False
        self.playing = False
        if self.stream.is_active():  
            self.stream.stop_stream()


    def close(self):
        self.stream.close()
        self.p.terminate()


recorder = Recorder()


def on_start():
    recorder.start_recording()
    print("Recording and playing started.")


def on_stop():
    recorder.stop_recording()
    print("Recording and playing stopped.")
    recorder.close()
    root.destroy()


root = tk.Tk()
root.title("Audio Recorder")

start_button = tk.Button(root, text="Start Recording", command=on_start)
start_button.pack()

stop_button = tk.Button(root, text="Stop Recording", command=on_stop)
stop_button.pack()

root.mainloop()
