from fastapi import APIRouter, Query, Form
from fastapi.responses import StreamingResponse
from grafos.grafo_aprendizado import criar_grafo_aprendizado
from agente.executor import perguntar_a_llm_stream

import json
import time
from datetime import datetime
import sqlite3
import os

router = APIRouter()
grafo, no_responder = criar_grafo_aprendizado()


@router.get("/treinar")
def treinar():
    estado = {"forcar_treino": True}
    grafo.executar(estado)
    return {"mensagem": "Aprendizado concluído."}

@router.post("/aprender_com_documentacao")
def aprender_com_documentacao(url: str = Form(..., description="URL da documentação")):
    estado = {"url": url, "forcar_treino": False}
    grafo.executar(estado)
    return {"mensagem": "Documentação aprendida com sucesso.", "url": url}


@router.post("/aprender_com_diretorio")
def aprender_com_diretorio(diretorio: str = Form(..., description="Caminho do diretório")):
    estado = {"diretorio": diretorio, "forcar_treino": True}
    grafo.executar(estado)
    return {"mensagem": "Documentação treinada com sucesso.", "diretorio": diretorio}



@router.get("/perguntar")
def perguntar(pergunta: str = Query(..., description="Faça uma pergunta ou peça código")):
    estado = {"pergunta": pergunta, "forcar_treino": False}
    grafo.executar(estado)
    resposta = estado.get("resposta", "Sem resposta.")
    
    # Salvar no histórico
    salvar_historico(pergunta, resposta)
    
    return {"resposta": resposta}


def init_historico_db():
    """Inicializa o banco de dados do histórico"""
    db_path = "historico.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def salvar_historico(pergunta: str, resposta: str):
    """Salva uma pergunta e resposta no histórico"""
    init_historico_db()
    
    db_path = "historico.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO historico (pergunta, resposta) VALUES (?, ?)",
        (pergunta, resposta)
    )
    
    conn.commit()
    conn.close()


@router.get("/historico")
def obter_historico():
    """Retorna o histórico de perguntas e respostas"""
    init_historico_db()
    
    db_path = "historico.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT pergunta, resposta, timestamp FROM historico ORDER BY timestamp DESC LIMIT 20"
    )
    
    resultados = cursor.fetchall()
    conn.close()
    
    historico = []
    for pergunta, resposta, timestamp in resultados:
        historico.append({
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": timestamp
        })
    
    return {"historico": historico}


@router.get("/perguntar_stream")
def perguntar_stream(pergunta: str = Query(..., description="Faça uma pergunta com streaming")):
    """Endpoint para perguntas com streaming direto da LLM"""
    
    def generate_response():
        # Enviar evento de início
        yield f"data: {json.dumps({'type': 'start'})}\n\n"
        
        # Processar pergunta e obter contexto
        estado = {"pergunta": pergunta, "forcar_treino": False}
        grafo.executar(estado)
        
        aprendiz = estado.get("aprendiz")
        contexto = estado.get("contexto", [])
        
        if contexto and aprendiz:
            # Usar streaming da LLM
            stream = perguntar_a_llm_stream(pergunta, contexto)
            resposta_completa = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    resposta_completa += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
            
            # Salvar no histórico
            salvar_historico(pergunta, resposta_completa)
        else:
            resposta = "Sem contexto relevante encontrado."
            yield f"data: {json.dumps({'type': 'chunk', 'content': resposta})}\n\n"
            salvar_historico(pergunta, resposta)
        
        # Enviar evento de fim
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )