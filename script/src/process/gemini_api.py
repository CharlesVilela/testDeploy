import os
from dotenv import load_dotenv
import google.generativeai as genai
import dao.mongo_connect as mongo_db
from process import question_similarity_and_message_analysis

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

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

def send_input_gemini_api(user_input):
    
    model = configure_gemini_api()
    # Carregar o histórico da conversa do banco de dados
    # history = mongo_db.get_all()
    # # Filtrar apenas as mensagens chave
    # key_messages = question.filter_key_messages(history)

    # Limitar o histórico às últimas 10 mensagens, por exemplo
    # max_history_length = 15
    # if len(history) > max_history_length:
    #     history = history[-max_history_length:]
    
    # biography_text = mongo_db.get_biography(user_input)
    # print()
    # print('SHOW BIOGRAPHY CONTEXT ', biography_text)
    # if biography_text:
    #     # Insere a biografia como uma "mensagem do sistema" para dar contexto ao modelo
    #     history.insert(0, {"role": "system", "parts": [biography_text]})
    
    # key_messages = history
    try:
        # Inicia a sessão de chat
        chat_session = model.start_chat()
        # Envia as mensagens do histórico
        # for message in key_messages:
        #     chat_session.send_message({
        #         "role": message["role"],
        #         "parts": message["parts"]
        #     })
        # Envia a pergunta do usuário
        print(user_input)
        response = chat_session.send_message({
            "role": "user",
            "parts": [user_input]
        })
        return response.text
    except Exception as e:
        print()
        return "Houve um error ao tentar mandar esta requisição para a API do Gemini, tente novamente!", {e}
