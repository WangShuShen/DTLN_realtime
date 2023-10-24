import tkinter as tk
import numpy as np
import sounddevice as sd
import tflite_runtime.interpreter as tflite
import threading
from scipy.signal import resample
import argparse


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-i', '--input-device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-o', '--output-device', type=int_or_str,
    help='output device (numeric ID or substring)')

parser.add_argument('--latency', type=float,
                    help='latency in seconds', default=0.01)
args = parser.parse_args(remaining)

# set some parameters
block_len_ms = 32
block_shift_ms = 8
fs_target = 16000

# create the interpreters
interpreter_1 = tflite.Interpreter(
    model_path='./pretrained_model/model_1.tflite')
interpreter_1.allocate_tensors()
interpreter_2 = tflite.Interpreter(
    model_path='./pretrained_model/model_2.tflite')
interpreter_2.allocate_tensors()

# Get input and output tensors.
input_details_1 = interpreter_1.get_input_details()
output_details_1 = interpreter_1.get_output_details()
input_details_2 = interpreter_2.get_input_details()
output_details_2 = interpreter_2.get_output_details()

# create states for the lstms
states_1 = np.zeros(input_details_1[1]['shape']).astype('float32')
states_2 = np.zeros(input_details_2[1]['shape']).astype('float32')

# calculate shift and length
block_shift = int(np.round(fs_target * (block_shift_ms / 1000)))
block_len = int(np.round(fs_target * (block_len_ms / 1000)))

# create buffer
in_buffer = np.zeros((block_len)).astype('float32')
out_buffer = np.zeros((block_len)).astype('float32')


class EnhancedRecorder:
    def __init__(self, chunk=6000, channels=1, rate=48000):
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.recording = False
        self.playing = False
        self.p = sd.Stream(device=(args.input_device, args.output_device),
                           samplerate=fs_target, blocksize=block_shift,
                           dtype=np.float32, latency=args.latency,
                           channels=1, callback=self.callback)

    def callback(self, indata, outdata, frames, time, status):

        global in_buffer, out_buffer, states_1, states_2
        if status:
            print(status)

        in_buffer[:-block_shift] = in_buffer[block_shift:]
        in_buffer[-block_shift:] = np.squeeze(indata)

        # calculate fft of input block
        in_block_fft = np.fft.rfft(in_buffer)
        in_mag = np.abs(in_block_fft)
        in_phase = np.angle(in_block_fft)

        # reshape magnitude to input dimensions
        in_mag = np.reshape(in_mag, (1, 1, -1)).astype('float32')

        # set tensors to the first model
        interpreter_1.set_tensor(input_details_1[1]['index'], states_1)
        interpreter_1.set_tensor(input_details_1[0]['index'], in_mag)

        # run calculation
        interpreter_1.invoke()

        # get the output of the first block
        out_mask = interpreter_1.get_tensor(output_details_1[0]['index'])
        states_1 = interpreter_1.get_tensor(output_details_1[1]['index'])

        # calculate the ifft
        estimated_complex = in_mag * out_mask * np.exp(1j * in_phase)
        estimated_block = np.fft.irfft(estimated_complex)

        # reshape the time domain block
        estimated_block = np.reshape(
            estimated_block, (1, 1, -1)).astype('float32')

        # set tensors to the second block
        interpreter_2.set_tensor(input_details_2[1]['index'], states_2)
        interpreter_2.set_tensor(input_details_2[0]['index'], estimated_block)

        # run calculation
        interpreter_2.invoke()

        # get output tensors
        out_block = interpreter_2.get_tensor(output_details_2[0]['index'])
        states_2 = interpreter_2.get_tensor(output_details_2[1]['index'])

        # write to buffer
        out_buffer[:-block_shift] = out_buffer[block_shift:]
        out_buffer[-block_shift:] = np.zeros((block_shift))
        out_buffer += np.squeeze(out_block)

        # output to soundcard
        enhanced_audio = np.expand_dims(
            out_buffer[:frames], axis=-1)  # Ensure the shape matches
        if enhanced_audio.shape[0] < outdata.shape[0]:  # Padding if necessary
            padding = np.zeros((outdata.shape[0] - enhanced_audio.shape[0], 1))
            enhanced_audio = np.vstack((enhanced_audio, padding))
        outdata[:] = enhanced_audio

    def start_recording(self):
        self.recording = True
        self.playing = True
        self.p.start()
        print("Recording and enhancing started.")

    def stop_recording(self):
        self.recording = False
        self.playing = False
        self.p.stop()
        print("Recording and enhancing stopped.")

    def close(self):
        self.p.close()


recorder = EnhancedRecorder()


def on_start():
    threading.Thread(target=recorder.start_recording).start()


def on_stop():
    recorder.stop_recording()
    recorder.close()
    root.destroy()


root = tk.Tk()
root.title("Enhanced Audio Recorder")

start_button = tk.Button(root, text="Start Recording", command=on_start)
start_button.pack()

stop_button = tk.Button(root, text="Stop Recording", command=on_stop)
stop_button.pack()

root.mainloop()
