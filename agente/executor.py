from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=OPENAI_API_KEY)

def perguntar_a_llm(pergunta, contexto):
    prompt = f"""
                Você é o Oráculo, Agente MAestro, um assistente virtual que pode responder perguntas sobre Tudo o que lhe for passado pelo:
                Contexto: {contexto}
                
                Responda a pergunta de forma concisa e clara:
                Pergunta: {pergunta}
                """
    resposta = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resposta.choices[0].message["content"]
    print('resposta:', resposta)



