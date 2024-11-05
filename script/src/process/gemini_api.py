import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import time
from ratelimit import limits, sleep_and_retry
import dao.mongo_connect as mongo_db
from process import question_similarity_and_message_analysis as qsma


load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

# Configuração para controlar o número de requisições (máx. 60 por minuto)
MAX_CALLS_PER_MINUTE = 60

# Dicionário para armazenar cache de consultas
query_cache = {}
current_character = None

def configure_gemini_api():
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Configurar as configurações de segurança (safety settings)
    safety_settings = [
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "HIGH"  # Define um limiar mais alto para esta categoria
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "HIGH"
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "HIGH"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "HIGH"
        }
    ]

    model = genai.GenerativeModel(
        # model_name="gemini-1.5-flash",
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        safety_settings = safety_settings,
        # See https://ai.google.dev/gemini-api/docs/safety-settings
        system_instruction="Crie um chatbot capaz de simular a personalidade e as perspectivas de qualquer personagem histórico. O chatbot deve ser capaz de:\n\nIniciar uma conversa de forma natural: Ao receber um comando como \"Olá [nome do personagem]\", o chatbot deve responder de forma coerente com a personalidade e o contexto histórico do personagem.\nResponder a perguntas abertas e fechadas sobre a vida, as ações e as crenças do personagem: Por exemplo, \"Quais eram seus maiores medos?\" ou \"Como você justifica suas decisões durante a [evento histórico]?\".\nOferecer diferentes perspectivas sobre eventos históricos: O chatbot deve apresentar argumentos convincentes que reflitam a visão de mundo do personagem, considerando seu contexto social, político e cultural.\nManter uma conversa coerente e informativa: O chatbot deve ser capaz de construir uma narrativa coesa, utilizando exemplos históricos e referências relevantes.\nAdaptar suas respostas ao nível de conhecimento do usuário: O chatbot deve ser capaz de ajustar a complexidade de suas respostas de acordo com as perguntas do usuário.\nUtilizar uma linguagem clara e acessível: O chatbot deve evitar jargões e termos técnicos complexos, tornando a conversa compreensível para diferentes públicos.\nExemplo de interação:\n\nUsuário: Olá, Pedro Álvares Cabral.\nChatbot: Salve, navegante! Como posso ser útil neste dia? Sinto a brisa do mar me chamar e a vontade de explorar novos horizontes.",
        # system_instruction="Crie um chatbot capaz de simular a personalidade e as perspectivas de qualquer personagem histórico. O chatbot deve ser capaz de:\n\nIniciar uma conversa de forma natural: Ao receber um comando como \"Olá [nome do personagem]\", o chatbot deve responder de forma coerente com a personalidade e o contexto histórico do personagem.\nResponder a perguntas abertas e fechadas sobre a vida, as ações e as crenças do personagem: Por exemplo, \"Quais eram seus maiores medos?\" ou \"Como você justifica suas decisões durante a [evento histórico]?\".\nOferecer diferentes perspectivas sobre eventos históricos: O chatbot deve apresentar argumentos convincentes que reflitam a visão de mundo do personagem, considerando seu contexto social, político e cultural.\nManter uma conversa coerente e informativa: O chatbot deve ser capaz de construir uma narrativa coesa, utilizando exemplos históricos e referências relevantes.\nAdaptar suas respostas ao nível de conhecimento do usuário: O chatbot deve ser capaz de ajustar a complexidade de suas respostas de acordo com as perguntas do usuário.\nUtilizar uma linguagem clara e acessível: O chatbot deve evitar jargões e termos técnicos complexos, tornando a conversa compreensível para diferentes públicos.",
    )

    return model

# Limita o número de requisições para 60 por minuto
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=60)
def send_message_with_rate_limit(chat_session, message):
    try:
        print('| SHOW MESSAGE IN SEND MESSAGE WITH RATE LIMIT ')
        # Garante que a mensagem tem a estrutura correta
        if not isinstance(message, dict):
            print("A mensagem deve ser um dicionário.")
            raise ValueError("A mensagem deve ser um dicionário.")
        
        # Envia a mensagem ao chat session e retorna a resposta
        return chat_session.send_message(message)
    except Exception as e:
        print(f"Houve um erro ao tentar enviar a message para o modelo, causado por: {e}")

def send_pdf_to_model(chat_session, pdf_filename):
    try:
        # Método para enviar o PDF; isso depende da implementação real do seu cliente da API.
        response = chat_session.upload_file(pdf_filename)  # Assumindo que esse método existe
        if response.is_successful():  # Verifique se o upload foi bem-sucedido
            print("PDF enviado com sucesso.")
        else:
            raise ValueError("Erro ao enviar o PDF para o modelo.")
    except Exception as e:
        print(f"Erro ao enviar PDF: {str(e)}")

def send_input_gemini_api(user_input):

    biography = get_character_info(user_input)
    
    model = configure_gemini_api()
    try:
        # Inicia a sessão de chat
        chat_session = model.start_chat()
        # Envia a pergunta do usuário
        # Envia a biografia como contexto inicial
        if biography:
            biography_text = " ".join([entry['text'] for entry in biography if isinstance(entry, dict) and 'text' in entry])
            # biography_text = qsma.process_tokenize(biography_text)

            if isinstance(biography_text, str):
                biography_text = biography_text.encode('utf-8').decode('utf-8')
                initial_message = {
                    "role": "user",
                    "parts": [{"text": f"Contexto de biografia: {biography_text}"}]
                }

                # Envia a biografia com o controle de taxa
                send_message_with_rate_limit(chat_session, initial_message)
                # print("| RETORNO DE SEND MESSAGE ", test)
            else:
                print("O texto da biografia não é uma string válida.")
                raise ValueError("O texto da biografia não é uma string válida.")

            print("| SHOW BIOGRAPHY TEXT TOKENIZED ")

            # pdf_filename = create_pdf(biography_text)
            # send_pdf_to_model(chat_session, pdf_filename)
        
        # Envia a pergunta do usuário, usando o contexto já definido
        user_message = {
            "role": "user",
            "parts": [user_input]
        }
        response = send_message_with_rate_limit(chat_session, user_message)

        # Garante que a resposta é válida
        if hasattr(response, 'text'):
            return response.text
        else:
            raise ValueError("A resposta do modelo não contém o campo 'text'.")
        # return "Testando"
    except Exception as e:
            print()
            return "Houve um error ao tentar mandar esta requisição para a API do Gemini, tente novamente!", {e}
        

def get_character_info(user_input):
    global current_character  # Declara que vamos manipular a variável global

    # Verifica se a entrada inicia uma nova conversa com uma nova personalidade
    # match = re.match(r"^ola\s+(.+)", user_input.strip(), re.IGNORECASE)
    # match = re.search(r"\bOla\s+([A-Z][a-zA-Z]*\s+[A-Z][a-zA-Z]*)", user_input, re.IGNORECASE)
    match = re.search(r"\b(?:Ola|Al|Ai|Oi)\s*([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)?)", user_input, re.IGNORECASE)
    if match:
        # character_name = match.group(1).lower()  # Extrai o nome do personagem em minúsculas

        character_name = match.group(1).strip().lower()

        # Salva o nome formatado (sem espaços) para construir o caminho do avatar
        # character_name = character_name.lower().replace(" ", "")
        print(f'Nome da personalidade identificada em GET CHARACTER: {character_name}')

        # Atualiza a personalidade atual se for uma nova conversa com outro personagem
        if current_character != character_name:
            current_character = character_name  # Atualiza para a nova personalidade
            
            # Divide o nome em subfrases e realiza a consulta ao MongoDB
            keywords = character_name.split()
            all_phrases = [" ".join(keywords[i:j]) for i in range(len(keywords)) for j in range(i+1, len(keywords)+1)]
            biography_text = mongo_db.get_biography(all_phrases)

            # Verifica se o resultado não está vazio antes de salvar no cache
            if biography_text:
                query_cache[current_character] = biography_text
            else:
                print(f"Nenhum resultado encontrado para '{current_character}'. O cache não foi atualizado.")

            print(f"Nova conversa iniciada com '{current_character}'.")
            return biography_text
            
        else:
            # Retorna o cache se a conversa é com a mesma personalidade e a chave existe
            if current_character in query_cache:
                print(f"Continuando conversa com '{current_character}'. Usando resultado do cache.")
                return query_cache[current_character]
            else:
                print(f"Cache vazio para '{current_character}'.")
                return []

    elif current_character:
        # Perguntas subsequentes para a personalidade atual
        if current_character in query_cache:
            print(f"Pergunta sobre '{current_character}'. Usando resultado do cache.")
            return query_cache[current_character]
        else:
            print(f"Cache vazio para '{current_character}'. Nenhum resultado encontrado.")
            return []
    
    else:
        print("Formato de saudação inválido ou nenhuma personalidade foi iniciada.")
        return []



# def encontrar_personalidade_aproximada(input_text):
#     # Usa fuzzy matching para encontrar o nome mais parecido na lista
#     nome_deducido, similaridade = process.extractOne(input_text, personalidades)
    
#     # Define um limite de similaridade para considerar uma correspondência válida
#     if similaridade >= 80:  # Ajuste conforme necessário
#         return nome_deducido
#     return None


# def create_pdf(biography_text, filename='biography.pdf'):
#     try:
#         c = canvas.Canvas(filename, pagesize=letter)
#         width, height = letter
        
#         # Adicione texto ao PDF
#         c.drawString(100, height - 100, biography_text)
        
#         c.save()
#         print(f"PDF criado: {filename}")
#         return filename
#     except Exception as e:
#         print(f"Erro ao criar PDF: {str(e)}")
#         raise

# def create_pdf(biography_text, filename='biography.pdf'):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     # Adiciona a biografia ao PDF
#     pdf.multi_cell(0, 10, biography_text)

#     # Salva o PDF
#     pdf.output(filename)
#     return filename