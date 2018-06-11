import os
import socket


HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SZIE = 1024

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSocket.connect(ADDR)

## recv streaming
def pcm2wav(path):
    os.system(('ffmpeg -f s16le -ar 16000 -ac 1 -i {} -ar 44100 -ac 2 {}.wav -y').format(path, path))

data = clientSocket.recv(BUFF_SZIE)
if data == b'tts':
    f = open('polly_tts', 'ab')
    while True:
        data = clientSocket.recv(BUFF_SZIE)
        if data[-3:] == b'end':
            f.write(data[:-3])
            f.close()
            break
        f.write(data)

pcm2wav('polly_tts')
os.unlink('polly_tts')
os.system('aplay polly_tts.wav')
