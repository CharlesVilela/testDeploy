import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from fuzzywuzzy import process


model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

nltk.download('punkt_tab')
nltk.download('stopwords')

def find_similar_question(new_question, previous_questions):
    new_embedding = model.encode(new_question)
    previous_embeddings = model.encode(previous_questions)
    cosine_similarities = cosine_similarity([new_embedding], previous_embeddings)
    max_similarity = max(cosine_similarities[0])
    most_similar_index = cosine_similarities[0].argmax()
    return most_similar_index, max_similarity


# Função adaptada para encontrar o nome de uma personalidade
def find_similar_personality(input_name, known_personalities):
    # Gera o embedding para o nome da personalidade inserido pelo usuário
    input_embedding = model.encode(input_name)
    print("| SHOW INPUT EMBEDDING ", input_name)

    # Gera uma lista de embeddings previamente calculados para os nomes das personalidades
    personality_embeddings = model.encode(known_personalities)
    print("| SHOW PERSONALITY EMBEDDING ", known_personalities)

    # Calcula a similaridade de coseno entre o nome inserido e os nomes conhecidos
    cosine_similarities = cosine_similarity([input_embedding], personality_embeddings)
    
    # Encontra o índice da personalidade mais similar e a pontuação de similaridade
    max_similarity = max(cosine_similarities[0])
    most_similar_index = cosine_similarities[0].argmax()
    
    # Define um limite de similaridade (ajuste conforme necessário)
    if max_similarity >= 0.8:
        return known_personalities[most_similar_index], max_similarity
    else:
        return None, max_similarity  # Retorna None se a similaridade for muito baixa


def find_most_similar_personality(input_name, personalities):
    # Usa fuzzywuzzy para encontrar a correspondência mais próxima
    best_match, similarity_score = process.extractOne(input_name, personalities)
    return best_match, similarity_score

def replace_in_prompt(prompt, incorrect_name, correct_name):
    # Substitui o nome incorreto pelo nome correto na frase
    return re.sub(r'\b' + re.escape(incorrect_name) + r'\b', correct_name, prompt, flags=re.IGNORECASE)

def is_key_message(message):
    """
        Função para determinar se uma mensagem é considerada chave ou importante
    """
    print("| -- SHOW MESSAGE IN IS_KEY_MESSAGE -- |")
    print(message)
    print("| ------------------------------------ |")
    keywords = ["história", "evento", "decisão", "motivo", "medo", "explicação"]
    # Verifica se a mensagem contém uma palavra-chave
    for keyword in keywords:
        if keyword in " ".join(message["parts"]).lower():
            print("| SHOW KEYWORD ", keyword)
            return True
    
    # Verifica se a mensagem é longa o suficiente para ser relevante
    if len(" ".join(message["parts"])) > 50: # Pode ajustar esse número
        return True

    return False

def filter_key_messages(history):
    """
        Filtra o histórico para incluir apenas as mensagens chave
    """
    return [message for message in history if is_key_message(message)]


def process_tokenize(input_text):
    # Tokenização
    words = word_tokenize(input_text)

    # Remoção de stop words
    stop_words = set(stopwords.words('portuguese'))  # Substitua por 'english' se necessário
    filtered_tokens = [word for word in words if word not in stop_words]

    # Stemming (opcional)
    # stemmer = nltk.stem.RSLPStemmer()  # Stemmer para português
    # stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]

    return filtered_tokens