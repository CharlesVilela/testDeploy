from pymongo import MongoClient, errors, server_api
import streamlit as st
from datetime import datetime

def connected_bd():
    uri = "mongodb+srv://charlesvilela:user@cluster0.ryzor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=server_api.ServerApi('1'), connectTimeoutMS=60000)
    try:
        client.admin.command('ping')
    except Exception as e:
        print(e)
    return client["chatbot_chronoschat"]


def insert_bd(new_interaction):
    db = connected_bd()
    collection = db["chatbot"]
    if collection is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return
    
    data = {"userquestion": new_interaction.user_question, 
             "botresponse": new_interaction.bot_response, 
             "userid": new_interaction.user_id, 
             "timeresponse": new_interaction.timestamp,
             "datetime": datetime.now(),
             "isQuestionAudio": new_interaction.isQuestionAudio,
             "isResponseAudio": new_interaction.isResponseAudio}
    try:
        result = collection.insert_one(data)
    except errors.ServerSelectionTimeoutError as e:
        st.error(f"Erro de timeout na seleção do servidor: {e}")
    except errors.ConnectionFailure as e:
        st.error(f"Erro de conexão com o MongoDB: {e}")
    except Exception as e:
        st.error(f"Erro inesperado ao inserir dados: {e}")


def get_all():
    db = connected_bd()
    collection = db["chatbot"]
    resultado = collection.find()

    if resultado is None:
        return

    history = []
    for doc in resultado:
        user_input = doc.get("userquestion", "")
        assitant_response = doc.get("botresponse", "")
        
        if user_input:
            history.append({
                "role": "user",
                "parts": [user_input]
            })
        if assitant_response:
            history.append({
                "role": "assistant",
                "parts": [assitant_response]
            })
    return history

# def get_previous_questions():
#     db = connected_bd()
#     collection = db["chatbot"]
#     return [doc['userquestion'] for doc in collection.find({}, {"userquestion": 1, "_id": 0})]

def get_previous_questions():
    db = connected_bd()
    collection = db["chatbot"]
    
    # Buscar tanto as perguntas quanto as respostas
    results = collection.find({}, {"userquestion": 1, "botresponse": 1, "_id": 0})
    
    # Retornar uma lista de dicionários com 'userquestion' e 'botresponse'
    return [{"question": doc['userquestion'], "response": doc['botresponse']} for doc in results]

def insert_history(history):
    db = connected_bd()
    collection = db["history"]

    if collection is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return
    
    try:
        result = collection.insert_one(history)
    except errors.ServerSelectionTimeoutError as e:
        st.error(f"Erro de timeout na seleção do servidor: {e}")
    except errors.ConnectionFailure as e:
        st.error(f"Erro de conexão com o MongoDB: {e}")
    except Exception as e:
        st.error(f"Erro inesperado ao inserir dados: {e}")

def get_history():
    db = connected_bd()
    collection = db["history"]
    resultado = collection.find()

    if resultado is None:
        return

    history = []
    for doc in resultado:
        user_input = doc.get("userquestion", "")
        history.append({
            "role": "user",
            "parts": [user_input]
        })
    return history


def get_biography(user_input):
    # Realizar uma pesquisa de texto com base nas palavras-chave do user_input
    try:
        db = connected_bd()
        collection = db["biography"]
        keywords = user_input.split()
        results = collection.find(
                {"keywords": {"$in": keywords}},  # Verifica se alguma palavra-chave está no array 'keywords'
                {"text": 1, "_id": 0}  # Apenas retorna o campo 'text' (o conteúdo da biografia)
        )
        biography_texts = " ".join([result["text"] for result in results])

        for result in results:
            print(result["text"])

        # Retorna os textos encontrados como uma lista
        print('| SHOW USER INPUT ', user_input)
        print('| SHOW KEYWORDS ', keywords)
        print('| SHOW FIND BIOGRAPHY ', biography_texts)
        return biography_texts if biography_texts else None
        
    except Exception as e:
        print(f"Erro ao buscar biografias: {e}")
        return []