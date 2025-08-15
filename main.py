from fastapi import FastAPI, Query
from banco.conexao import criar_tabela, criar_tabela_conhecimento
from agente.aprendiz import Aprendiz
from grafos.grafo_aprendizado import criar_grafo_aprendizado

app = FastAPI(title="Aprendiz Mastre")

DIRETORIO = "/app/dados"
criar_tabela()
criar_tabela_conhecimento()
aprendiz = Aprendiz(DIRETORIO)
grafo, no_responder = criar_grafo_aprendizado()


@app.get("/treinar")
def treinar():
    estado = {}
    grafo.executar(estado)
    return {"mensagem": "Aprendizado concluído!"}

@app.get("/perguntar")
def perguntar(pergunta: str = Query(...)):
    estado = {"pergunta": pergunta}
    grafo.executar(estado)
    return {"resposta": estado.get("resposta", "Não sei responder")}
