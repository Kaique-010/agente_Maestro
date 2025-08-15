from agente import aprendiz

from .grafo_base import No


def criar_grafo_aprendizado():
    def no_aprender(estado):
        aprendiz.aprender()
        estado["absorvido"] = True
        return estado


    def no_responder(estado):
        pergunta = estado.get("pergunta", "")
        estado["resposta"] = aprendiz.consultar(pergunta)
        return estado

    raiz = No("raiz", None)
    no_aprender = No("aprender", no_aprender)
    no_responder = No("responder", no_responder)
    raiz.ligar(no_aprender)
    no_aprender.ligar(no_responder)
    return raiz, no_responder
