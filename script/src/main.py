import re
import uuid
import time
import streamlit as st
import threading

from queue import Queue
from datetime import datetime
from io import BytesIO
from util import interaction
from collections import deque
from audio_recorder_streamlit import audio_recorder

from dao import mongo_connect
from process import question_similarity_and_message_analysis
from audio import process_audio
import audio.process_audio as pa
import process.gemini_api as api

def main():
    st.set_page_config(page_title='ChronosChat', page_icon=':assistant:')
    st.header("ChronoChat")

    isPrimary_question = True
    messages = st.container()
    isQuestionAudio = False

     # Inicializar estados
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = {"status": False}
    if "frames" not in st.session_state:
        st.session_state.frames = []
    if "audio_thread" not in st.session_state:
        st.session_state.audio_thread = None
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    if "isconverter_texto_audio" not in st.session_state:
        st.session_state.isconverter_texto_audio = False

    # Inicializar a fila de mensagens se ainda não existir
    if 'chatbot_responses' not in st.session_state:
        st.session_state.chatbot_responses = deque()  # Usar deque como fila
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
        st.session_state['start_time'] = time.time()
    # Rastrear interações
    if 'interactions' not in st.session_state:
        st.session_state['interactions'] = []
    
    if isPrimary_question:
        messages.chat_message("assistant").write("Olá no que posso te ajudar hoje?")
    
    
    audio_transcript = ""
    with st.sidebar:
        on = st.toggle("Ativar respostas em audio")

        if "prev_speech_hash" not in st.session_state:
            st.session_state.prev_speech_hash = None

        speech_input = audio_recorder(
                                    "Precione para falar:", 
                                    icon_size="3x", 
                                    neutral_color="#6ca395", 
                                    energy_threshold = ( - 1.0 ,  1.0 ), 
                                    pause_threshold = 3.0 ,
                                    )
        if speech_input and st.session_state.prev_speech_hash != hash(speech_input):
            st.session_state.prev_speech_hash = hash(speech_input)
            process_audio.save_audio_file(speech_input, "audio.wav")
            audio_transcript = process_audio.audio_to_text("audio.wav")
            isQuestionAudio = True



    # Entrada do usuário
    if (prompt := st.chat_input("Diga alguma coisa")) or (prompt := audio_transcript):
        isPrimary_question = False
        spinner_message = "Hummmm... Deixe-me pensar"

        # Adiciona a pergunta do usuário à fila de interações e exibe
        st.session_state.chatbot_responses.append({
            "role": "user",
            "content":[{
                "type": "text",
                "text": prompt,
            }]
        })

        with st.spinner(spinner_message):
            # Formatar a data e hora sem caracteres inválidos
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            isResponseAudio = False
            # Gerar a resposta do chatbot
            previous_data = mongo_connect.get_previous_questions()
            previous_questions = [item['question'] for item in previous_data]
            index, similarity = question_similarity_and_message_analysis.find_similar_question(prompt, previous_questions)
            if similarity > 0.8:
                response = previous_data[index]['response']
            else:
                response = api.send_input_gemini_api(prompt)

            # Checa se a conversão para áudio está ativada
            if on:
                audio_path = f"script\\output\\audio_output_{st.session_state['user_id']}_{timestamp}.wav"
                audio = process_audio.text_to_audio(response, save_path=audio_path)
                st.session_state.chatbot_responses.append({
                    "role": "assistant",
                    "content":[{
                        "type": "audio_file",
                        "audio_file": audio_path,
                    }]
                })

                isResponseAudio = True

            else:
                # Adiciona a resposta do assistente em texto à fila
                st.session_state.chatbot_responses.append({
                    "role": "assistant",
                    "content":[{
                        "type": "text",
                        "text": response,
                    }]
                })

            interaction.log_interaction(prompt, response, isQuestionAudio, isResponseAudio)

     # Exibir todas as interações na tela, em pares de pergunta e resposta
    for message in st.session_state.chatbot_responses:
        with st.chat_message(message["role"]):
            for content in message["content"]:
                if content["type"] == "text":
                    st.write(content["text"])
                elif content["type"] == "audio_file":
                    st.audio(content["audio_file"])

   

if __name__ == '__main__':
    main()
