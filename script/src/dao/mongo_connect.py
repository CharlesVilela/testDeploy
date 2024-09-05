from pymongo import MongoClient, errors
import streamlit as st

def connected_bd():
    try:
        client = MongoClient("mongodb+srv://charlesvilela:user@cluster0.ryzor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["chatbot_chronoschat"]
        collection = db["chatbot"]
        return collection
    except errors.ServerSelectionTimeoutError as e:
        st.error(f"Erro ao conectar ao MongoDB: {e}")
        return None



def insert_bd(new_interaction):
    # Exemplo de inserção de dados

    collection = connected_bd()
    dados = {"userquestion": new_interaction.user_question, 
             "botresponse": new_interaction.bot_response, 
             "userid": new_interaction.user_id, 
             "timeresponse": new_interaction.timestamp}
    
    print("| SHOW DADOS DO USUARIO: ", dados)
    print()
    print("| SHOW DA COLLECTION RETORNADO: ", collection)
    print()
    print("| SHOW TIMESTAMP: ", new_interaction.timestamp)
    print()
    
    collection.insert_one(dados)
    get_all()

def get_all():
    # Exemplo de consulta
    print("| FIND ALL DADOS NO BANCO MONGO DB ATLAS... |")
    collection = connected_bd()

    resultado = collection.find()
    # Exibindo os dados
    for dado in resultado:
        print(dado)
