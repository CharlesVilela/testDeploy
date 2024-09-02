import re
import uuid
import time
import streamlit as st
import threading

import audio.process_audio as pa
import process.gemini_api as api
from util import interaction

def main():
    st.set_page_config(page_title='Pergunte para mim...', page_icon=':books:')
    st.header("ChronoChat")

    # Adicionando estilo CSS para ajustar a altura dos botões
    st.markdown("""
        <style>
        .stButton > button {
            height: 50px;
            margin-top: 63px;
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)
    
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
        st.session_state['start_time'] = time.time()
    # Rastrear interações
    if 'interactions' not in st.session_state:
        st.session_state['interactions'] = []
    # Inicializar estados
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = {"status": False}
    if "frames" not in st.session_state:
        st.session_state.frames = []
    if "audio_thread" not in st.session_state:
        st.session_state.audio_thread = None
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "chatbot_response" not in st.session_state:
        st.session_state.chatbot_response = ""
    if "isconverter_texto_audio" not in st.session_state:
        st.session_state.isconverter_texto_audio = False

    # Criar colunas para organizar o layout
    col1, col2 = st.columns([1, 1])

    with col1:
        # Botão para converter resposta em áudio
        st.session_state.isconverter_texto_audio = st.checkbox("Converter Resposta em Áudio", value=st.session_state.isconverter_texto_audio)

        user_input = st.text_input("Ask a Question from the PDF Files", value=st.session_state.user_input)
        # Exibir texto reconhecido, se disponível
        if st.session_state.recognized_text:
            st.text_area("Texto Reconhecido", st.session_state.recognized_text, height=150)
        
        # Atualizar o estado com a pergunta do usuário
        if user_input != st.session_state.user_input:
            st.session_state.user_input = user_input

    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            if st.button("Iniciar Gravação"):
                if not st.session_state.is_recording["status"]:
                    st.session_state.is_recording = {"status": True}
                    st.session_state.frames = []
                    st.session_state.audio_thread = threading.Thread(target=pa.record_audio, args=(st.session_state.frames, st.session_state.is_recording))
                    st.session_state.audio_thread.start()
                    st.warning("Gravando áudio...")

        with col2_2:
            if st.button("Parar Gravação"):
                with st.spinner("Gerando resposta..."):
                    if st.session_state.is_recording["status"]:
                        st.session_state.is_recording["status"] = False
                        st.session_state.audio_thread.join()
                        pa.save_audio(st.session_state.frames, "audio.wav")
                        st.success("Áudio gravado e salvo como audio.wav")

                        # Converter áudio em texto
                        text = pa.audio_to_text("audio.wav")
                        # st.session_state.recognized_text = text

                        # Atualizar pergunta do usuário com o texto reconhecido
                        if text:
                            st.session_state.user_input = text

    # Processar a pergunta do usuário e gerar resposta
    if st.session_state.user_input:
        if st.session_state.user_input != "":
            with st.spinner("Gerando resposta..."):
                user_input = st.session_state.user_input
                response = api.send_input_gemini_api(user_input)
                st.session_state.chatbot_response = response.text

                interaction.log_interaction(user_input, response.text)

            # Limpar a pergunta do usuário após obter a resposta
            st.session_state.user_input = ""

    # Exibir a resposta do chatbot
    if st.session_state.chatbot_response:
        if st.session_state.isconverter_texto_audio:
            cleaned_response = re.sub(r'[^\w\s]', '', st.session_state.chatbot_response)
            audio_file = pa.text_to_audio(cleaned_response)
            st.audio(audio_file, format='audio/mp3')
        else:
            st.write("Reply:")
            st.markdown(f'<div style="width: 100%; margin-top: 10px; background-color: #f9f9f9; padding: 10px; border-radius: 5px;">{st.session_state.chatbot_response} 😊</div>', unsafe_allow_html=True)
    
    # # Capturar o tempo final ao encerrar a sessão
    # if st.button("Finalizar Sessão"):
    #     session_duration = time.time() - st.session_state['start_time']
    #     # database.log_session(st.session_state.user_id, session_duration)
    #     st.success(f"Sessão finalizada. Duração: {session_duration:.2f} segundos")

if __name__ == '__main__':
    main()
