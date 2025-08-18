import os
from agente.aprendiz import Aprendiz
from grafos.grafo_base import No
from config import DIRETORIO_DADOS

def criar_grafo_aprendizado():
    def no_aprender(estado):
        aprendiz = Aprendiz(DIRETORIO_DADOS)
        
        # Se há diretório específico, só processa ele
        if estado.get("diretorio"):
            aprendiz.aprender_com_diretorio(estado["diretorio"])
        # Se há URL, processa documentação
        elif estado.get("url"):
            aprendiz.aprender_com_documentacao_web(estado["url"])
        # Se há arquivo específico, processa ele
        elif estado.get("arquivo"):
            aprendiz.aprender_com_arquivo(estado["arquivo"])
        # Só treina o diretório padrão se não há entrada específica
        elif estado.get("forcar_treino", True):
            aprendiz.aprender(reset=True)
        
        estado["aprendiz"] = aprendiz
        return estado

    def no_filtrar(estado):
        pergunta = estado.get("pergunta", "")
        aprendiz = estado.get("aprendiz")
        estado["contexto"] = aprendiz.buscar_contexto_relevante(pergunta, limite=12) if pergunta else []
        return estado

    def no_responder(estado):
        pergunta = estado.get("pergunta", "")
        if not pergunta:
            estado["resposta"] = "Pergunta vazia."
            return estado
        aprendiz = estado.get("aprendiz")
        pares = estado.get("contexto", [])
        estado["resposta"] = aprendiz.consultar(pergunta) if pares else "Sem contexto relevante encontrado."
        return estado

    raiz = No("raiz", None)
    n1 = No("aprender", no_aprender)
    n2 = No("filtrar", no_filtrar)
    n3 = No("responder", no_responder)

    raiz.ligar(n1).ligar(n2).ligar(n3)
    return raiz, n3
