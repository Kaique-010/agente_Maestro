import sqlite3
import json
import math
from typing import List, Tuple
from config import SQLITE_PATH


def _conn():
    return sqlite3.connect(SQLITE_PATH)

def criar_tabelas():
    con = _conn()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        linguagem TEXT,
        resumo TEXT,
        embedding TEXT
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_path ON conhecimento(path);")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fontes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        resumo TEXT,
        linguagem TEXT
    );
    """)
    # Nova tabela para memórias de embedding
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memorias_embedding (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        embedding TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    con.commit()
    con.close()

def limpar_conhecimento():
    con = _conn()
    con.execute("DELETE FROM conhecimento;")
    con.commit()
    con.close()

def salvar_conhecimento(path: str, resumo: str, linguagem: str, embedding: list):
    con = _conn()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO conhecimento(path, linguagem, resumo, embedding)
        VALUES(?,?,?,?)
    """, (path, linguagem, resumo, json.dumps(embedding)))
    con.commit()
    con.close()

def obter_conhecimento(limit=500) -> List[Tuple[str,str,str,list]]:
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT path, linguagem, resumo, embedding FROM conhecimento LIMIT ?", (limit,))
    rows = cur.fetchall()
    con.close()
    return [(path, linguagem, resumo, json.loads(embedding)) for path, linguagem, resumo, embedding in rows]


def _cosine(a, b):
    # a e b são listas de floats
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0: return 0.0
    return dot / (na * nb)

def buscar_por_embedding(emb_consulta: list, limite=10):
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT path, resumo, embedding FROM conhecimento")
    candidatos = []
    for path, resumo, emb_json in cur.fetchall():
        emb = json.loads(emb_json)
        score = _cosine(emb_consulta, emb)
        candidatos.append((score, path, resumo))
    con.close()
    candidatos.sort(reverse=True, key=lambda x: x[0])
    top = [(p, r) for _, p, r in candidatos[:limite]]
    return top

def obter_estatisticas_por_linguagem():
    """
    Retorna estatísticas de aprendizado por linguagem
    Returns: List[Tuple[str, int, float]] - (linguagem, quantidade, percentual)
    """
    con = _conn()
    cur = con.cursor()
    
    # Contar total de arquivos
    cur.execute("SELECT COUNT(*) FROM conhecimento")
    total = cur.fetchone()[0]
    
    if total == 0:
        con.close()
        return []
    
    # Contar por linguagem
    cur.execute("""
        SELECT linguagem, COUNT(*) as quantidade 
        FROM conhecimento 
        GROUP BY linguagem 
        ORDER BY quantidade DESC
    """)
    
    resultados = []
    for linguagem, quantidade in cur.fetchall():
        percentual = (quantidade / total) * 100
        resultados.append((linguagem or "Desconhecido", quantidade, percentual))
    
    con.close()
    return resultados


def obter_todos_arquivos():
    """
    Retorna todos os arquivos conhecidos
    Returns: List[Dict[str, str]] - (caminho, resumo, linguagem)
    """
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT path, resumo, linguagem FROM conhecimento")
    rows = cur.fetchall()
    con.close()
    return [(path, resumo, linguagem) for path, resumo, linguagem in rows]

def obter_todas_fontes():
    """
    Retorna todas as fontes conhecidas
    Returns: List[Dict[str, str]] - (url, resumo, linguagem)
    """
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT url, resumo, linguagem FROM fontes")
    rows = cur.fetchall()
    con.close()
    return [(url, resumo, linguagem) for url, resumo, linguagem in rows]

def salvar_fonte(url: str, resumo: str, linguagem: str):
    """Salva uma fonte de aprendizado."""
    con = _conn()
    cur = con.cursor()
    cur.execute("INSERT INTO fontes (url, resumo, linguagem) VALUES (?, ?, ?)", (url, resumo, linguagem))
    con.commit()
    con.close()


def salvar_memoria_embedding(pergunta: str, resposta: str):
    """Registra a memória de embedding."""
    from utils.embeddings import gerar_embedding
    import json
    
    con = _conn()
    cur = con.cursor()
    
    # Gerar embedding da pergunta
    embedding = gerar_embedding(pergunta)
    
    cur.execute(
        "INSERT INTO memorias_embedding (pergunta, resposta, embedding) VALUES (?, ?, ?)", 
        (pergunta, resposta, json.dumps(embedding))
    )
    con.commit()
    con.close()

def obter_memorias_embedding(limite=50):
    """Retorna memórias de embedding armazenadas."""
    con = _conn()
    cur = con.cursor()
    cur.execute(
        "SELECT pergunta, resposta, embedding, timestamp FROM memorias_embedding ORDER BY timestamp DESC LIMIT ?", 
        (limite,)
    )
    rows = cur.fetchall()
    con.close()
    return [(pergunta, resposta, json.loads(embedding), timestamp) for pergunta, resposta, embedding, timestamp in rows]

def buscar_memoria_por_embedding(emb_consulta: list, limite=5):
    """Busca memórias similares por embedding."""
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT pergunta, resposta, embedding FROM memorias_embedding")
    candidatos = []
    for pergunta, resposta, emb_json in cur.fetchall():
        emb = json.loads(emb_json)
        score = _cosine(emb_consulta, emb)
        candidatos.append((score, pergunta, resposta))
    con.close()
    candidatos.sort(reverse=True, key=lambda x: x[0])
    return [(p, r) for _, p, r in candidatos[:limite]]
