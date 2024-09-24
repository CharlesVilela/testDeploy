import time
import streamlit as st
from datetime import datetime
from dao import mongo_connect as mongo_db
from model import interaction_entity

# Função para registrar interações
def log_interaction(user_question, bot_response):
    # Crie uma instância da classe Interaction
    new_interaction = interaction_entity.Interaction(
        timestamp=get_time_spent(),
        user_id=st.session_state['user_id'],
        user_question=user_question,
        bot_response=bot_response
    )
    mongo_db.insert_bd(new_interaction)

    

# Rastrear tempo na página
def get_time_spent():
    end_time = time.time()
    total_time = end_time - st.session_state['start_time']
    return total_time