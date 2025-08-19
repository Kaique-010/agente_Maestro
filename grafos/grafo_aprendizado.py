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
    
    def listar_aprendizado(estado):
        aprendiz = estado.get("aprendiz")
        if aprendiz:
            estado["resposta"] = aprendiz.listar_conceitos()
        else:
            estado["resposta"] = "Nenhum aprendizado encontrado."
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

    def no_decisor(estado):
        """Decide se deve listar conceitos ou responder pergunta"""
        pergunta = estado.get("pergunta", "")
        listar_conceitos = estado.get("listar_conceitos", False)
        
        if listar_conceitos or not pergunta:
            # Se foi solicitado listar conceitos ou não há pergunta, executa listagem
            return listar_aprendizado(estado)
        else:
            # Se há pergunta, executa o fluxo de resposta
            estado = no_filtrar(estado)
            return no_responder(estado)

    raiz = No("raiz", None)
    n1 = No("aprender", no_aprender)
    n2 = No("decisor", no_decisor)

    # Conectar o fluxo principal
    raiz.ligar(n1)
    n1.ligar(n2)
    
    return raiz, n2
