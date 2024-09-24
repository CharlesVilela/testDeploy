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
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 2
#     RATE = 44100

#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)

#     while is_recording["status"]:
#         data = stream.read(CHUNK)
#         frames.append(data)

#     stream.stop_stream()
#     stream.close()
#     audio.terminate()



def save_audio(frames, filename):
    # Verifique se há dados nos frames
    if len(frames) == 0:
        raise ValueError("Nenhum dado de áudio foi gravado.")

    # Converta a lista de numpy arrays em um único array
    audio_data = np.concatenate(frames, axis=0)

    # Parâmetros do áudio
    num_channels = 1  # Mono
    sample_width = 2  # Para áudio de 16-bit
    frame_rate = 48000  # Usando a mesma taxa de amostragem da gravação

    # Escreva os dados de áudio em um arquivo .wav
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(frame_rate)
        wf.writeframes(audio_data.tobytes())



import sounddevice as sd
import numpy as np

def record_audio(filename, duration=10, device=None, channels=1, samplerate=44100):
    """
    Grava um arquivo de áudio.

    Args:
        filename: Nome do arquivo de saída.
        duration: Duração da gravação em segundos.
        device: Índice do dispositivo de áudio (opcional).
        channels: Número de canais (1 para mono, 2 para estéreo).
        samplerate: Taxa de amostragem.
    """

    chunk_size = 1024
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(f'Error recording: {status}')
        recording.append(indata.copy())

    try:
        with sd.InputStream(samplerate=samplerate,
                            channels=channels,
                            blocksize=chunk_size,
                            device=device,
                            callback=callback):
            print('Começando a gravação...')
            sd.sleep(int(duration * 1000))
            print('Gravação encerrada.')

        # Concatenar os frames em um único array
        data = np.concatenate(recording)

        # Salvar o arquivo de áudio (ajuste o formato conforme necessário)
        sd.write(filename, data, samplerate=samplerate, channels=channels)

    except Exception as e:
        print(f'Erro durante a gravação: {e}')





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

def text_to_audio(text, lang='pt', save_path=None):
    with open(save_path, 'wb') as audio_fp:
        tts = gTTS(text=text, lang=lang)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        if save_path:
            with open(save_path, 'wb') as f:
                f.write(audio_fp.getvalue())

    return save_path

