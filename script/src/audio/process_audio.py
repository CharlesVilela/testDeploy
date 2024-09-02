import wave
import speech_recognition as sr
import numpy as np
from gtts import gTTS
from io import BytesIO
import sounddevice as sd


# Função para salvar o áudio
# def save_audio(frames, filename):
#     wf = wave.open(filename, 'wb')
#     wf.setnchannels(2)
#     wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
#     wf.setframerate(44100)
#     wf.writeframes(b''.join(frames))
#     wf.close()


# Função para gravar áudio
# def record_audio(frames, is_recording):
    # CHUNK = 1024
    # FORMAT = pyaudio.paInt16
    # CHANNELS = 2
    # RATE = 44100

    # audio = pyaudio.PyAudio()
    # stream = audio.open(format=FORMAT, channels=CHANNELS,
    #                     rate=RATE, input=True,
    #                     frames_per_buffer=CHUNK)

    # while is_recording["status"]:
    #     data = stream.read(CHUNK)
    #     frames.append(data)

    # stream.stop_stream()
    # stream.close()
    # audio.terminate()



def save_audio(frames, filename):
    # Convert list of numpy arrays to a single numpy array
    audio_data = np.concatenate(frames, axis=0)

    # Get audio parameters
    num_channels = 2
    sample_width = 2  # For 16-bit audio
    frame_rate = 44100

    # Write audio data to a .wav file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(frame_rate)
        wf.writeframes(audio_data.tobytes())



def record_audio(frames, is_recording):
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    def callback(indata, frames, time, status):
        if status:
            print(status)
        frames.append(indata.copy())

    # Start the recording stream
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, blocksize=CHUNK, callback=callback):
        while is_recording["status"]:
            sd.sleep(100)  # Keep the recording active for as long as the status is True

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