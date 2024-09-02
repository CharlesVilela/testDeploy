import wave
import pyaudio
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO


# Função para salvar o áudio
def save_audio(frames, filename):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()


# Função para gravar áudio
def record_audio(frames, is_recording):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    while is_recording["status"]:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()


# Função para converter áudio em texto
def audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='pt-BR')
        except sr.UnknownValueError:
            text = "Não foi possível entender o áudio."
        except sr.RequestError as e:
            text = f"Erro na requisição ao serviço de reconhecimento de fala: {e}"
    return text

def text_to_audio(text, lang='pt'):
    tts = gTTS(text=text, lang=lang)
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    return audio_fp