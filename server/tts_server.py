import socket
import os

from boto3 import client


HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(ADDR)
serverSocket.listen(5)

while True:
    clientSocket, addr = serverSocket.accept()
    print("Connected from", addr)

    data = 'tts'
    clientSocket.send(data.encode())

    polly = client("polly", region_name="ap-northeast-2")
    response = polly.synthesize_speech(
        Text="안녕하세요",
        SampleRate="16000",
        OutputFormat="pcm",
        VoiceId="Seoyeon")
    stream = response.get("AudioStream")
    data = stream.read()
    print("Polly PCM")
    clientSocket.sendall(data)
    print("Success Polly PCM Streaming")

    data = 'end'
    clientSocket.send(data.encode())
