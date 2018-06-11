import os

from boto3 import client


def pcm2wav(path):
    os.system(('ffmpeg -f s16le -ar 16000 -ac 1 -i {} -ar 44100 -ac 2 {}.wav -y').format(path, path))

polly = client("polly", region_name="ap-northeast-2")
response = polly.synthesize_speech(
    Text="안녕하세요",
    SampleRate="16000",
    OutputFormat="pcm",
    VoiceId="Seoyeon")
stream = response.get("AudioStream")

with open('polly_tts', 'wb') as f:
    data = stream.read()
    print(data)
    f.write(data)

pcm2wav('polly_tts')

