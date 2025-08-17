from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL, MAX_ARQUIVOS_CONTEXT
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT_SISTEMA = """Você é um desenvolvedor sênior especialista em Django (DRF) e React Native.
Gere código seguindo EXATAMENTE os padrões do contexto: nomes, organização, imports e bibliotecas.
Não invente libs. Mantenha o estilo consistente com o projeto de referência.
Responda com trechos de código completos e explicação curta quando necessário."""

def perguntar_a_llm(pergunta, contexto_pairs):
    # contexto_pairs: List[(path, resumo)]
    contexto_fmt = []
    for path, resumo in contexto_pairs[:MAX_ARQUIVOS_CONTEXT]:
        contexto_fmt.append(f"ARQUIVO: {path}\nPADROES:\n{resumo}\n---")
    contexto_txt = "\n".join(contexto_fmt)

    mensagens = [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": f"Contexto de referência:\n{contexto_txt}\n\nPergunta:\n{pergunta}"}
    ]
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=mensagens,
        temperature=0
    )
    return resp.choices[0].message.content
