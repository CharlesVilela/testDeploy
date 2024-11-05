import re
import uuid
import os
import time
import streamlit as st
import threading
import random

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

# BIBLIOTECAS NOVAS INSTALADAS
#  - fuzzywuzzy
#  - python-Levenshtein

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
    if 'current_avatar' not in st.session_state:
        # st.session_state['current_avatar'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image", "default.jpeg") 
        st.session_state['current_avatar'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "default.jpeg")
    if 'personality_exist' not in st.session_state:
        st.session_state['personality_exist'] = False
    if 'personality_name' not in st.session_state:
         st.session_state['personality_name'] = None
    if 'random_personality' not in st.session_state:
        st.session_state['random_personality'] = []
    if isPrimary_question:
        messages.chat_message("assistant").write("✨ Bem-vindo(a) ao nosso Portal Temporal! ✨ Prepare-se para embarcar em conversas extraordinárias com as grandes figuras da história! Nossa máquina do tempo está pronta para conectar você com pensadores brilhantes, líderes audaciosos e mentes visionárias de eras passadas. 🌌")
    
    
    audio_transcript = ""
    with st.sidebar:
        # on = st.toggle("Ativar respostas em audio")
        on = False

        if "prev_speech_hash" not in st.session_state:
            st.session_state.prev_speech_hash = None

        # speech_input = audio_recorder(
        #                             "Precione para falar:", 
        #                             icon_size="3x", 
        #                             neutral_color="#6ca395", 
        #                             energy_threshold = ( - 1.0 ,  1.0 ), 
        #                             pause_threshold = 3.0 ,
        #                             )
        speech_input = None
        if speech_input and st.session_state.prev_speech_hash != hash(speech_input):
            st.session_state.prev_speech_hash = hash(speech_input)
            process_audio.save_audio_file(speech_input, "audio.wav")
            audio_transcript = process_audio.audio_to_text("audio.wav")
            isQuestionAudio = True



    # Entrada do usuário
    if (prompt := st.chat_input("Diga: Olá [NOME DA PERSONALIDADE]. Exemplo: Olá Ada Lovelace")) or (prompt := audio_transcript):
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
            prompt = re.sub(r"[^\w\sÀ-ÿ]", "", prompt)
            prompt = interaction.accent_remover(prompt)

            # match = re.search(r"\bOla\s+([A-Z][a-zA-Z]*\s+[A-Z][a-zA-Z]*)", prompt, re.IGNORECASE)
            match = re.search(r"\b(?:Ola|Al|Ai|Oi)\s*([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)?)", prompt, re.IGNORECASE)
            print("| SHOW MATCH ", match)
            if match:
                character_name = match.group(1).strip()
                print("| SHOW CHARACTER NAME BY SIMILAR PERSONALITIES ", character_name)

                st.session_state['personality_name'] = character_name
                list_personality_and_image = mongo_connect.get_all_personalities()
                list_only_personality = [p['personality'] for p in list_personality_and_image]

                st.session_state['random_personality'] = random.sample(list_only_personality, min(4, len(list_only_personality)))

                
                deduced_name, similarity = question_similarity_and_message_analysis.find_most_similar_personality(character_name, list_only_personality)
                
                if similarity > 70:
                    print(f"Nome deduzido: {deduced_name} (max similaridade: {similarity:.2f}) (similaridade: {similarity:.2f})")
                    prompt = question_similarity_and_message_analysis.replace_in_prompt(prompt, character_name, deduced_name)
                    st.session_state['personality_exist'] = True
                    character_avatar_name = None
                    for personality in list_personality_and_image:
                        if personality["personality"].lower() == deduced_name:
                            character_avatar_name = personality["image"]


                    avatar_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", f"{character_avatar_name}")
                    # Verifica se o avatar existe; se existir, atualiza o avatar atual
                    print('| PATH EXISTS ', os.path.exists(avatar_path))
                    if os.path.exists(avatar_path):
                        st.session_state['current_avatar'] = avatar_path
                        print(f'Avatar atualizado para: {character_name}')
                    else:
                        st.session_state['current_avatar'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "default.jpeg")
                        print(f'Avatar não encontrado para: {character_name}')

                else:
                    print(f"Nenhuma correspondência suficientemente próxima foi encontrada. (similaridade: {similarity:.2f})")
                    st.session_state['current_avatar'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "image", "default.jpeg")
                    st.session_state['personality_exist'] = False

            isResponseAudio = False
            # Gerar a resposta do chatbot
            previous_data = mongo_connect.get_previous_questions()
            previous_questions = [item['question'] for item in previous_data]
            index, similarity = question_similarity_and_message_analysis.find_similar_question(prompt, previous_questions)
            # if similarity > 0.8:
            if False:
                print('ENTROU NAS PERGUNTAS SIMILARES')
                response = previous_data[index]['response']
            else:
                print("| SHOW PROMPT QUE CHEGOU PARA ENVIAR PARA O GEMINI ", prompt)
                if st.session_state['personality_exist']:
                    response = api.send_input_gemini_api(prompt)
                else:
                    response = f"Parece que nossa máquina do tempo ainda não conseguiu calibrar as coordenadas para visitar {st.session_state['personality_name']}. Estamos trabalhando para ajustar nossos mecanismos e em breve esperamos tornar essa viagem possível! Enquanto isso, que tal explorar outras eras ou conversar com outra figura histórica? Como: {st.session_state['random_personality']}. Nossa linha do tempo tem muitos destinos fascinantes à sua espera!"
                

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
                st.session_state.chatbot_responses.append({
                    "role": "assistant",
                    "content":[{
                        "type": "text",
                        "text": response,
                    }],
                    "avatar": st.session_state['current_avatar']
                })

            interaction.log_interaction(prompt, response, isQuestionAudio, isResponseAudio)

    #  # Exibir todas as interações na tela, em pares de pergunta e resposta
    # for message in st.session_state.chatbot_responses:
    #     with st.chat_message(message["role"]):
    #         for content in message["content"]:
    #             if message["role"] == "assistant":
    #                 st.image(message["avatar"],width=50)
    #             if content["type"] == "text":
    #                 st.write(content["text"])
    #             elif content["type"] == "audio_file":
    #                 st.audio(content["audio_file"])
    # Exibir todas as interações na tela, em pares de pergunta e resposta
    for message in st.session_state.chatbot_responses:
        if message["role"] == "assistant":
            # Exibe a imagem do avatar no lugar do ícone padrão
            # Altere o papel temporariamente para evitar o ícone
            if message.get("avatar"):
                st.image(message["avatar"], width=50)
            else:
                st.chat_message(message["role"])
            for content in message["content"]:
                    if content["type"] == "text":
                        st.write(content["text"])
                    elif content["type"] == "audio_file":
                        st.audio(content["audio_file"])
        else:
            with st.chat_message(message["role"]):
                for content in message["content"]:
                    if content["type"] == "text":
                        st.write(content["text"])
                    elif content["type"] == "audio_file":
                        st.audio(content["audio_file"])

   

if __name__ == '__main__':
    main()
