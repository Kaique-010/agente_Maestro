from openai import OpenAI
from config import OPENAI_API_KEY, EMB_MODEL


_client = OpenAI(api_key=OPENAI_API_KEY)

def gerar_embedding(texto: str):
    # texto pode ser grande; mandamos resumo já tratado
    resp = _client.embeddings.create(
        input=texto,
        model=EMB_MODEL
    )
    return resp.data[0].embedding
