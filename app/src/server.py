import pyaudio
import wave
from flask import Flask
server = Flask(__name__)

@server.route("/")
def hello():
    return "Hello World!"

@server.route("/startRecording")
def startRecording():
    # Record in chunks of 1024 samples
    chunk = 2048 
    
    # 16 bits per sample
    sample_format = pyaudio.paInt16 
    chanels = 1
    
    # Record at 44100 samples per second
    smpl_rt = 44100
    seconds = 2
    filename = "/src/recordingtest.wav"
    
    # Create an interface to PortAudio
    pa = pyaudio.PyAudio()
    
    stream = pa.open(format=sample_format, channels=chanels,
                    rate=smpl_rt, input=True,
                    frames_per_buffer=chunk)
    
    print('Recording...')
    
    # Initialize array to be used for storing frames
    frames = [] 
    
    # Store data in chunks for 8 seconds
    for i in range(0, int(smpl_rt / chunk * seconds)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    
    # Terminate - PortAudio interface
    pa.terminate()
    
    print('Done !!! ')
    
    # Save the recorded data in a .wav format
    sf = wave.open(filename, 'wb')
    sf.setnchannels(chanels)
    sf.setsampwidth(pa.get_sample_size(sample_format))
    sf.setframerate(smpl_rt)
    sf.writeframes(b''.join(frames))
    sf.close()
    return "CallComplete"


if __name__ == "__main__":
   server.run(debug=True, host='0.0.0.0')
