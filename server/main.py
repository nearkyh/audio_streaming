# -*- coding:utf-8 -*-

import socket
import os
import time

from ffmpy import FFmpeg

from utils import speech_to_text    # Google STT
from utils import aibril_connector  # Aibril Conversation
from boto3 import client            # AWS-Polly TTS


def pcm2wav(path):
    ff = FFmpeg(
            inputs={path: ['-f', 's16le', '-ar', '44100', '-ac', '2']},
            outputs={''.join([path, '.wav']): '-y'})
    ff.run()

HOST = ''
PORT = 7100
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

serverSocket = socket.socket()
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind(ADDR)
serverSocket.listen(5)

stt_conn = speech_to_text.SpeechToText()
aibril_conn = aibril_connector.WatsonServer()

while True:
    clientSocket, addr = serverSocket.accept()
    print("Connected from", addr)

    # receive streaming data
    start_time = time.time()
    data = clientSocket.recv(BUFF_SIZE)
    if data == b'rec':
        f = open('record', 'ab')
        while True:
            data = clientSocket.recv(BUFF_SIZE)
            if data[-3:] == b'end':
                f.write(data[:-3])
                f.close()
                break
            f.write(data)
    pcm_recv_time = time.time() - start_time

    start_time = time.time()
    pcm2wav('record')
    os.unlink('record')
    pcm2wav = time.time() - start_time

    # stt
    start_time = time.time()
    text = stt_conn.audio_stt('record.wav')
    stt_time = time.time() - start_time

    # conversation
    start_time = time.time()
    answer = aibril_conn.aibril_conv(text)
    conv_time = time.time() - start_time

    # tts
    data = 'tts'
    clientSocket.send(data.encode())
    start_time = time.time()

    polly = client("polly", region_name="ap-northeast-2")
    response = polly.synthesize_speech(
        Text=answer,
        SampleRate="16000",
        OutputFormat="pcm",
        VoiceId="Seoyeon")
    stream = response.get("AudioStream")
    data = stream.read()
    clientSocket.sendall(data)
    print("Success Polly PCM Streaming")

    data = 'end'
    clientSocket.send(data.encode())
    pcm_send_time = time.time() - start_time

    print("1. Received pcm data     >>", pcm_recv_time)
    print("2. pcm to wav            >>", pcm2wav)
    print("3. stt time              >>", stt_time)
    print("4. conversation time     >>", conv_time)
    print("5. Sending pcm data(tts) >>", pcm_send_time)
