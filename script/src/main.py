import re
import uuid
import time
import streamlit as st
import threading

import audio.process_audio as pa
import process.gemini_api as api
from util import interaction
from collections import deque

# def main():
#     st.set_page_config(page_title='Pergunte para mim...', page_icon=':books:')
#     st.header("ChronoChat")

#     # Inicializar a lista de mensagens se ainda não existir
#     if 'chatbot_responses' not in st.session_state:
#         st.session_state.chatbot_responses = []

#     messages = st.container(height=450)
#     if prompt := st.chat_input("Say something"):
#         messages.chat_message("user").write(prompt)
#         # st.session_state.chatbot_responses.append(prompt)
#         with st.spinner("Gerando resposta..."):
#             # user_input = st.session_state.user_input
#             response = api.send_input_gemini_api(prompt)
#             # messages.chat_message("assistant").write(f"Echo: {response}")    

#             st.session_state.chatbot_responses.append(response)
#             # Loop para exibir todas as respostas acumuladas
#             for msg in st.session_state.chatbot_responses:
#                 messages.chat_message("assistant").write(f"Chatbot: {msg}")

def main():
    st.set_page_config(page_title='Pergunte para mim...', page_icon=':books:')
    st.header("ChronoChat")

    # Inicializar a fila de mensagens se ainda não existir
    if 'chatbot_responses' not in st.session_state:
        st.session_state.chatbot_responses = deque()  # Usar deque como fila
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
        st.session_state['start_time'] = time.time()
    # Rastrear interações
    if 'interactions' not in st.session_state:
        st.session_state['interactions'] = []


    messages = st.container()

    # Entrada do usuário
    if prompt := st.chat_input("Say something"):
        # Adicionar a pergunta do usuário à fila e exibir na tela
        # messages.chat_message("user").write(prompt)
        st.session_state.chatbot_responses.append(("user", prompt))

        with st.spinner("Gerando resposta..."):
            # Gerar a resposta do chatbot (substitua pela sua chamada real de API)
            response = api.send_input_gemini_api(prompt)
            st.session_state.chatbot_responses.append(("assistant", response))
            interaction.log_interaction(prompt, response)
    
        # Exibir todas as interações na tela, em ordem
        for message in st.session_state.chatbot_responses:
            # Verifique se cada item é uma tupla com dois elementos
            if isinstance(message, tuple) and len(message) == 2:
                role, msg = message
                if role == "user":
                    messages.chat_message("user").write(msg)
                elif role == "assistant":
                    messages.chat_message("assistant").write(msg)
            else:
                st.warning("Formato de mensagem inválido na fila.")
    

    # on = st.toggle("Activate feature")



if __name__ == '__main__':
    main()
