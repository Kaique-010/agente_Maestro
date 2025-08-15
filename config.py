import os 
from dotenv import load_dotenv

load_dotenv()

#configuração para o banco de dados
DB_PATH= "memoria.db"
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
LLM_MODEL = "gpt-4o-mini"
SMITHERY_API_KEY = os.getenv("SMITHERY_API_KEY")
