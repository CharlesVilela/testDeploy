from pymongo import MongoClient

def connected_bd():
    # Substitua com sua URL de conexão MongoDB
    client = MongoClient("mongodb+srv://charlesvilela:user@cluster0.ryzor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    # Escolha o banco de dados
    db = client["chatbot_chronoschat"]

    # Escolha a coleção
    collection = db["chatbot"]

    return collection

def insert_bd(new_interaction):
    # Exemplo de inserção de dados

    collection = connected_bd()
    dados = {"userquestion": new_interaction.user_question, 
             "botresponse": new_interaction.bot_response, 
             "userid": new_interaction.user_id, 
             "timeresponse": new_interaction.timestamp}
    
    collection.insert_one(dados)

def get_all():
    # Exemplo de consulta

    collection = connected_bd()

    resultado = collection.find()
    print(resultado)
