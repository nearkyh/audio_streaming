import os
import socket
import pyaudio
import time


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SEC = 3

HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

### send streaming ###
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSocket.connect(ADDR)

start_time = time.time()
data = 'rec'
clientSocket.send(data.encode())

for i in range(0, int(RATE / CHUNK * RECORD_SEC)):
  try:
    clientSocket.sendall(stream.read(CHUNK))
  except Exception as e:
    print(e)

data = 'end'
clientSocket.send(data.encode())

stream.stop_stream()
stream.close()
audio.terminate()
rec_time = time.time() - start_time

### recv streaming ###
def pcm2wav(path):
    os.system(('ffmpeg -f s16le -ar 16000 -ac 1 -i {} -ar 44100 -ac 2 {}.wav -y').format(path, path))

start_time = time.time()
data = clientSocket.recv(BUFF_SIZE)
if data == b'tts':
    f = open('polly_tts', 'ab')
    while True:
        data = clientSocket.recv(BUFF_SIZE)
        if data[-3:] == b'end':
            f.write(data[:-3])
            f.close()
            break
        f.write(data)
pcm_recv_time = time.time() - start_time

start_time = time.time()
pcm2wav('polly_tts')
pcm2wav = time.time() - start_time
os.unlink('polly_tts')
os.system('aplay polly_tts.wav')

print("1. Recording time         >>", rec_time)
print("2. Received pcm data(tts) >>", pcm_recv_time)
print("3. pcm to wav             >>", pcm2wav)

clientSocket.close()

