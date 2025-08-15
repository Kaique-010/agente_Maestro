from leitor.leitor_diretorio import ler_diretorio_aprendizado
from memoria.memoria_sqlite import obter_conhecimento
from .executor import perguntar_a_llm


class Aprendiz:
    def __init__(self, diretorio: str):
        self.diretorio = diretorio
        self.conhecimento = obter_conhecimento()
        print("Aprendiz inicializado")
    
    def aprender(self):
        total, json_files, readme_files = ler_diretorio_aprendizado(self.diretorio)
        print(f"Total de arquivos processados: {total}")
        print(f"JSON files: {json_files}")
        print(f"README files: {readme_files}")
        print(f"[Aprendiz] Aprendeu {total} arquivos.")
    
    def consultar(self, pergunta: str):
        contexto = obter_conhecimento()
        print("Contexto sendo passado para a LLM:")
        print(contexto)
        resposta = perguntar_a_llm(pergunta, contexto)
        print(f"[Aprendiz] Resposta: {resposta}")
        return resposta

