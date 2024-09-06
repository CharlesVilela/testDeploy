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
    collection = connected_bd()

    if collection is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    dados = {"userquestion": new_interaction.user_question, 
             "botresponse": new_interaction.bot_response, 
             "userid": new_interaction.user_id, 
             "timeresponse": new_interaction.timestamp}
    
    try:
        result = collection.insert_one(dados)
        st.success("Dados inseridos com sucesso!")
    except errors.ServerSelectionTimeoutError as e:
        st.error(f"Erro de timeout na seleção do servidor: {e}")
    except errors.ConnectionFailure as e:
        st.error(f"Erro de conexão com o MongoDB: {e}")
    except Exception as e:
        st.error(f"Erro inesperado ao inserir dados: {e}")

def get_all():
    # Exemplo de consulta
    print("| FIND ALL DADOS NO BANCO MONGO DB ATLAS... |")
    collection = connected_bd()

    resultado = collection.find()
    # Exibindo os dados
    for dado in resultado:
        print(dado)
