import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # bom para geração de código com custo ok
EMB_MODEL = os.getenv("EMB_MODEL", "text-embedding-3-small")

# Caminho no Docker ou local
DIRETORIO_DADOS = "/app/dados" if os.path.exists("/app/dados") else "./dados"
SQLITE_PATH = os.getenv("SQLITE_PATH", "./conhecimento.db")

# Limites
MAX_ARQUIVOS_CONTEXT = int(os.getenv("MAX_ARQUIVOS_CONTEXT", "12"))
MAX_TOKENS_POR_ARQ = int(os.getenv("MAX_TOKENS_POR_ARQ", "2000"))
