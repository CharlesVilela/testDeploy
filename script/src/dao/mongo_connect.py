from pymongo import MongoClient, errors, server_api
import streamlit as st

def connected_bd():
    uri = "mongodb+srv://charlesvilela:user@cluster0.ryzor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=server_api.ServerApi('1'), connectTimeoutMS=60000)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    return client["chatbot_chronoschat"]


def insert_bd(new_interaction):
    db = connected_bd()
    collection = db["chatbot"]

    if collection is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    dados = {"userquestion": new_interaction.user_question, 
             "botresponse": new_interaction.bot_response, 
             "userid": new_interaction.user_id, 
             "timeresponse": new_interaction.timestamp}

    try:
        result = collection.insert_one(dados)
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
        history.append({
            "role": "user",
            "parts": [user_input]
        })
    return history

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