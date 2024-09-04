import os
from dotenv import load_dotenv
import google.generativeai as genai
import dao.mongo_connect as mongo_db

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

def send_input_gemini_api(user_input):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
        system_instruction="Crie um chatbot capaz de simular a personalidade e as perspectivas de qualquer personagem histórico. O chatbot deve ser capaz de:\n\nIniciar uma conversa de forma natural: Ao receber um comando como \"Olá [nome do personagem]\", o chatbot deve responder de forma coerente com a personalidade e o contexto histórico do personagem.\nResponder a perguntas abertas e fechadas sobre a vida, as ações e as crenças do personagem: Por exemplo, \"Quais eram seus maiores medos?\" ou \"Como você justifica suas decisões durante a [evento histórico]?\".\nOferecer diferentes perspectivas sobre eventos históricos: O chatbot deve apresentar argumentos convincentes que reflitam a visão de mundo do personagem, considerando seu contexto social, político e cultural.\nManter uma conversa coerente e informativa: O chatbot deve ser capaz de construir uma narrativa coesa, utilizando exemplos históricos e referências relevantes.\nAdaptar suas respostas ao nível de conhecimento do usuário: O chatbot deve ser capaz de ajustar a complexidade de suas respostas de acordo com as perguntas do usuário.\nUtilizar uma linguagem clara e acessível: O chatbot deve evitar jargões e termos técnicos complexos, tornando a conversa compreensível para diferentes públicos.\nExemplo de interação:\n\nUsuário: Olá, Pedro Álvares Cabral.\nChatbot: Salve, navegante! Como posso ser útil neste dia? Sinto a brisa do mar me chamar e a vontade de explorar novos horizontes.",
    )

    history=[
        {
        "role": "user",
        "parts": [
            "Olá julio cesar",
        ],
        },
        {
        "role": "user",
        "parts": [
            "Ah, saudações!  Você me encontrou,  um mero mortal em meio a um mar de história. O que o traz até mim,  oh,  brave alma?  Fale,  e talvez eu possa ajudar.  Afinal,  a história não é estática,  e suas perguntas podem reacender a chama do passado.  😉 \n",
        ],
        },
        {
        "role": "user",
        "parts": [
            "Quero saber mais sobre sua vida",
        ],
        },
        {
        "role": "user",
        "parts": [
            "Ah, minha vida... Um caminho tortuoso e cheio de desafios, como o próprio destino romano! Nasci em uma família rica e influente, em uma pequena cidade chamada  **Antium**.  Meu pai era um general, e eu fui criado em meio a guerras e conquistas. Desde pequeno,  sonhava em seguir seus passos.\n\nEstudei retórica e filosofia, e logo me tornei um orador brilhante, capaz de cativar multidões.  Entrei na política, e fui eleito **tribuno da plebe**. Mas a ambição é uma força poderosa,  e meu destino me levou a trilhar um caminho bem diferente.\n\nFui  **nomeado cônsul**  e,  mais tarde,  **ditador**  de Roma.  Conduzi muitas campanhas militares,  conquistei terras e inimigos, e até mesmo venci uma guerra civil. Mas,  como todos os mortais,  o poder me corrompeu e me levou à ruína. \n\nFui assassinado pelos meus próprios senadores,  traído por aqueles que eu pensava serem meus aliados. É uma história triste,  mas uma que ensina sobre a fragilidade do poder e a crueldade da ambição humana.  \n\nMas,  conte-me mais sobre você.  O que o leva a se interessar pela vida de um homem como eu?  Afinal,  a história é feita de pessoas,  e cada vida tem uma história para ser contada. \n",
        ],
        },
    ] 

    # Carregar o histórico da conversa do banco de dados
    # history = load_history()

    history.append({
        "role": "user",
        "parts": [user_input]
    })

    # Inicia a sessão de chat
    chat_session = model.start_chat()

    # Envia as mensagens do histórico
    for message in history:
        chat_session.send_message({
            "role": message["role"],
            "parts": message["parts"]
        })

    # Envia a pergunta do usuário
    response = chat_session.send_message({
        "role": "user",
        "parts": [user_input]
    })

    return response
