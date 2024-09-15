import re
import uuid
import time
import streamlit as st
import threading

from io import BytesIO
import audio.process_audio as pa
import process.gemini_api as api
from util import interaction
from collections import deque
from dao import mongo_connect
from process import question_similarity_and_message_analysis
from audio import process_audio

def main():
    st.set_page_config(page_title='ChronosChat', page_icon=':assistant:')
    st.header("ChronoChat")

    isPrimary_question = True
    messages = st.container()

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
    
    
    with st.sidebar:
        on = st.toggle("Activate feature")

    print(on)

    # Entrada do usuário
    if prompt := st.chat_input("Say something"):
        isPrimary_question = False
         # Adicionar a pergunta do usuário à fila e exibir na tela
        st.session_state.chatbot_responses.append(("user", prompt))
        with st.spinner("Gerando resposta..."):
            # Gerar a resposta do chatbot (substitua pela sua chamada real de API)
            previous_data = mongo_connect.get_previous_questions()
            # Separar as perguntas para comparação
            previous_questions = [item['question'] for item in previous_data]

            index, similarity = question_similarity_and_message_analysis.find_similar_question(prompt, previous_questions)
            if similarity > 0.8:
                print("As perguntas foram similares...")
                response = previous_data[index]['response']
                interaction.log_interaction(prompt, response)
                if on:
                    audio = process_audio.text_to_audio(response)
                    st.audio(audio, format="audio/wav")
                    st.session_state.chatbot_responses.append(("assistant_audio", audio))
                else:
                    st.session_state.chatbot_responses.append(("assistant", response))
            else:
                print("As perguntas não foram similares...")
                response = api.send_input_gemini_api(prompt)
                interaction.log_interaction(prompt, response)
                if on:
                    audio = process_audio.text_to_audio(response)
                    st.audio(audio, format="audio/wav")
                    st.session_state.chatbot_responses.append(("assistant_audio", audio))
                else:
                    st.session_state.chatbot_responses.append(("assistant", response))
        
         # Exibir todas as interações na tela, em ordem
        for message in st.session_state.chatbot_responses:
            # Verifique se cada item é uma tupla com dois elementos
            if isinstance(message, tuple) and len(message) == 2:
                role, msg = message
                if role == "user":
                     messages.chat_message("user").write(msg)
                elif role == "assistant":
                    messages.chat_message("assistant").write(msg)
                elif role == "assistant_audio":
                    # Garante que 'message' seja um objeto BytesIO e não uma tupla
                    if isinstance(message, BytesIO):
                        st.audio(message, format="audio/wav") 
            else:
                st.warning("Formato de mensagem inválido na fila.")
        

if __name__ == '__main__':
    main()
