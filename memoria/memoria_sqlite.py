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

def obter_conhecimento(limit=500) -> List[Tuple[str,str,str]]:
    con = _conn()
    cur = con.cursor()
    cur.execute("SELECT path, linguagem, resumo FROM conhecimento LIMIT ?", (limit,))
    rows = cur.fetchall()
    con.close()
    return rows

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
