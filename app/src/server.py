import contextlib
import queue
import sys
import tempfile
import threading
import json
import time
import numpy as np
import sounddevice as sd
import soundfile as sf

from datetime import datetime
from time import sleep

from flask import Flask
from flask import jsonify

server = Flask(__name__)
app = None

class Status:
    HTTPStatus = 0
    isRecording = False
    timeStarted = 0
    def __init__(self):
        self.HTTPStatus = None
        self.isRecording = False
        self.timeStarted = None

status = Status()

@server.route("/")
def hello():
    return "Hello World!"

@server.route("/startRecording")
def startRecording():
    print('/startRecording called.')
    global app
    if app is None:
          app = RecGui()
    app.on_rec()

    status.HTTPStatus = 200
    status.isRecording = True
    status.timeStarted = int(time.time())
    return json.dumps(status.__dict__)

@server.route("/stopRecording")
def stopRecording():
    print('/stopRecording called.')
    app.on_stop()
    
    status.HTTPStatus = 200
    status.isRecording = False
    return json.dumps(status.__dict__)

@server.route("/status")
def getStatus():
    print('/getStatus called.')
    jsonStr = json.dumps(status.__dict__)
    return jsonStr

def file_writing_thread(*, q, **soundfile_args):
    """Write data from queue to file until *None* is received."""
    # NB: If you want fine-grained control about the buffering of the file, you
    #     can use Python's open() function (with the "buffering" argument) and
    #     pass the resulting file object to sf.SoundFile().
    with sf.SoundFile(**soundfile_args) as f:
        while True:
            data = q.get()
            if data is None:
                break
            f.write(data)
class RecGui():

    stream = None
    
    def __init__(self):
        # We try to open a stream with default settings first, if that doesn't
        # work, the user can manually change the device(s)
        self.create_stream()

        self.recording = self.previously_recording = False
        self.audio_q = queue.Queue()
        self.peak = 0
        self.metering_q = queue.Queue(maxsize=1)

        
    def create_stream(self, device=None):
        if self.stream is not None:
            self.stream.close()
        print("checking input settings for device 1")
        sd.check_input_settings(device=1, channels=1, samplerate=44100)
        self.stream = sd.InputStream(device=1, channels=1, samplerate=44100, callback=self.audio_callback)
        print("done create")
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status.input_overflow:
            # NB: This increment operation is not atomic, but this doesn't
            #     matter since no other thread is writing to the attribute.
            self.input_overflows += 1
        # NB: self.recording is accessed from different threads.
        #     This is safe because here we are only accessing it once (with a
        #     single bytecode instruction).
        if self.recording:
            self.audio_q.put(indata.copy())
            self.previously_recording = True
        else:
            if self.previously_recording:
                self.audio_q.put(None)
                self.previously_recording = False

        self.peak = max(self.peak, np.max(np.abs(indata)))
        try:
            self.metering_q.put_nowait(self.peak)
        except queue.Full:
            pass
        else:
            self.peak = 0

    def on_rec(self):
        print('/startRecording class method called.')
        self.recording = True

        now = datetime.now()

        filename = open("../recordings/rec_" + now.strftime("%m%d%Y_%H%M%S" + ".wav"), 'wb')
        #filename = tempfile.mktemp(
        #    prefix='delme_rec_gui_', suffix='.wav', dir='../recordings')

        if self.audio_q.qsize() != 0:
            print('WARNING: Queue not empty!')
        self.thread = threading.Thread(
            target=file_writing_thread,
            kwargs=dict(
                file=filename,
                mode='x',
                samplerate=int(self.stream.samplerate),
                channels=self.stream.channels,
                q=self.audio_q,
            ),
        )
        self.thread.start()

    def on_stop(self, *args):
        self.recording = False
        self.wait_for_thread()

    def wait_for_thread(self):
        sleep(0.1)
        self._wait_for_thread

    def _wait_for_thread(self):
        if self.thread.is_alive():
            self.wait_for_thread()
            return
        self.thread.join()

    def close_window(self):
        if self.recording:
            self.on_stop()
        self.destroy()

if __name__ == "__main__":
    print('STARTUP: STARTING WEB SERVER!')
    server.run(debug=True, host='0.0.0.0')