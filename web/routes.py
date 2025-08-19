from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from grafos.grafo_aprendizado import criar_grafo_aprendizado

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

grafo, no_responder = criar_grafo_aprendizado()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "resposta": None})


@router.post("/api/perguntar")
async def perguntar(request: Request, pergunta: str = Form(...)):
    estado = {"pergunta": pergunta, "forcar_treino": False}
    grafo.executar(estado)
    if estado.get("resposta") == no_responder:
        estado["resposta"] = "Desculpe, não entendi. Pode reformular a pergunta?"
    else:
        estado["resposta"] = estado.get("resposta", "Sem resposta.")
    return templates.TemplateResponse("index.html", {"request": request, "resposta": estado.get("resposta", "Sem resposta.")})

@router.post("/api/treinar")
async def treinar(request: Request):
    estado = {"forcar_treino": True}
    grafo.executar(estado)
    return {"mensagem": "Aprendizado concluído."}

@router.post("/api/aprender_com_documentacao")
async def aprender_com_documentacao(request: Request, url: str = Form(...)):
    estado = {"url": url, "forcar_treino": False}
    grafo.executar(estado)
    return templates.TemplateResponse("index.html", {"request": request, "resposta": "Documentação aprendida com sucesso."})

@router.post("/api/aprender_com_diretorio")
async def aprender_com_diretorio(request: Request, diretorio: str = Form(...)):
    estado = {"diretorio": diretorio, "forcar_treino": True}
    grafo.executar(estado)
    return {"mensagem": "Diretório aprendido com sucesso.", "diretorio": diretorio}
    return templates.TemplateResponse("index.html", {"request": request, "resposta": "Documentação treinada com sucesso."})

@router.get("/api/listar_conceitos")
async def listar_conceitos(request: Request):
    estado = {"forcar_treino": False}
    grafo.executar(estado)
    aprendizado = estado.get("aprendiz")
    if aprendizado:
        estatisticas = aprendizado.listar_conceitos()
        
        # Formatar as estatísticas como lista de strings
        conceitos = []
        total_arquivos = sum(quantidade for _, quantidade, _ in estatisticas)
        
        for linguagem, quantidade, percentual in estatisticas:
            conceitos.append(f"{quantidade} arquivos de {linguagem} ({percentual:.1f}% do total)")
        
        if conceitos:
            mensagem = f"Total de {total_arquivos} arquivos aprendidos em {len(estatisticas)} linguagens."
        else:
            mensagem = "Nenhum aprendizado encontrado."
    else:
        conceitos = []
        mensagem = "Nenhum aprendizado encontrado."
    return {"conceitos": conceitos, "mensagem": mensagem}

@router.get("/api/historico")
async def historico(request: Request):
    # Por enquanto retornando histórico vazio, pode ser implementado futuramente
    return {"historico": []}

@router.post("/api/listar_conceitos")
async def listar_conceitos(request: Request):
    estado = {"forcar_treino": False, "listar_conceitos": True}
    grafo.executar(estado)
    conceitos = estado.get("resposta", "Nenhum aprendizado encontrado.")
    return {"conceitos": conceitos}



