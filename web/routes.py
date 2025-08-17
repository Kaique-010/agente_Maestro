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


@router.post("/perguntar")
async def perguntar(request: Request, pergunta: str = Form(...)):
    estado = {"pergunta": pergunta, "forcar_treino": False}
    grafo.executar(estado)
    if estado.get("resposta") == no_responder:
        estado["resposta"] = "Desculpe, não entendi. Pode reformular a pergunta?"
    else:
        estado["resposta"] = estado.get("resposta", "Sem resposta.")
    return templates.TemplateResponse("index.html", {"request": request, "resposta": estado.get("resposta", "Sem resposta.")})

@router.get("/treinar")
async def treinar(request: Request):
    estado = {"forcar_treino": True}
    grafo.executar(estado)
    return templates.TemplateResponse("index.html", {"request": request, "resposta": "Aprendizado concluído."})

@router.post("/aprender_com_documentacao")
async def aprender_com_documentacao(request: Request, url: str = Form(...)):
    estado = {"url": url, "forcar_treino": False}
    grafo.executar(estado)
    return templates.TemplateResponse("index.html", {"request": request, "resposta": "Documentação aprendida com sucesso."})





