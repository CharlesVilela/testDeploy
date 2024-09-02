import pymysql

def connected_bd():
    # Conectar ao banco de dados
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="chatbot"
    )

def insert_bd(new_interaction):
    print('-- INSERT IN DATABASE --')
    
    conn = connected_bd()
    cursor = conn.cursor()

    # Definir os dados a serem inseridos
    data = (new_interaction.user_question, new_interaction.bot_response, new_interaction.user_id, new_interaction.timestamp)

    print(" ----------- ")
    print('| SHOW DATA |')
    print(data)
    print(" ----------- ")

    # Criar a instrução SQL INSERT, sem especificar o campo `id`
    sql = """
    INSERT INTO tblinteraction (userquestion, botresponse, userid, timeresponse)
    VALUES (%s, %s, %s, %s)
    """

    try:
        # Executar a instrução SQL
        cursor.execute(sql, data)

        # Confirmar a transação
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        # Fechar o cursor e a conexão
        cursor.close()
        conn.close()

def query_bd():
    conn = connected_bd()
    cursor = conn.cursor()

    # Executar uma consulta
    cursor.execute("SELECT * FROM tblinteraction")

    print("-- Consultando os dados no banco MYSQL --")
    # Buscar os resultados
    resultados = cursor.fetchall()
    for resultado in resultados:
        print(resultado)
    
    # Fechar o cursor e a conexão
    cursor.close()
    conn.close()
