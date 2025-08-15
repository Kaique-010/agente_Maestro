from banco.conexao import conectar, fechar_conexao

def obter_conhecimento():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT caminho, conteudo FROM conhecimento")

    conhecimentos = cursor.fetchall()
    fechar_conexao(conn)
    return conhecimentos

def obter_conhecimento_especifico(caminho: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT caminho, conteudo FROM conhecimento WHERE caminho = ?", (caminho,))
    conhecimento = cursor.fetchone()
    fechar_conexao(conn)
    return conhecimento

def obter_conhecimento_por_tipo(tipo: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT caminho, conteudo FROM conhecimento WHERE caminho LIKE ?", (f"%{tipo}%",))
    conhecimentos = cursor.fetchall()
    fechar_conexao(conn)
    return conhecimentos

def obter_conhecimento_por_conteudo(conteudo: str):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT caminho, conteudo FROM conhecimento WHERE conteudo LIKE ?", (f"%{conteudo}%",))
    conhecimentos = cursor.fetchall()
    fechar_conexao(conn)
    return conhecimentos

