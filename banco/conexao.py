import sqlite3
from config import DB_PATH

def conectar():
    conn = sqlite3.connect(DB_PATH)
    return conn

def fechar_conexao(conn):
    conn.close()

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rota TEXT,
        mensagem TEXT
    )
    ''')
    conn.commit()
    fechar_conexao(conn)

def criar_tabela_conhecimento():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caminho TEXT,
        conteudo TEXT
    )
    ''')
    conn.commit()
    fechar_conexao(conn)


