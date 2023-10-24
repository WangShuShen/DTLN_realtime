import sounddevice as sd

devices = sd.query_devices()
for i, device in enumerate(devices):
    print(f"Device ID: {i}")
    print(f"Device Name: {device['name']}")
    print(f"Input Channels: {device['max_input_channels']}")
    print(f"Output Channels: {device['max_output_channels']}")
    print(f"Default Sample Rate: {device['default_samplerate']}")
    print("-" * 50)
