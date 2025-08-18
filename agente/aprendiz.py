import requests
from bs4 import BeautifulSoup
from leitor.leitor_diretorio import ler_diretorio_aprendizado
from memoria.memoria_sqlite import (
    criar_tabelas, limpar_conhecimento, salvar_conhecimento,
    buscar_por_embedding, obter_conhecimento
)
from utils.extrator_codigo import extrair_info_arquivo
from utils.embeddings import gerar_embedding
from agente.executor import perguntar_a_llm

def extrair_conteudo_documentacao(url: str) -> str:
    """Extrai conteúdo de uma página de documentação."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts e estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extrai texto principal
        text = soup.get_text()
        
        # Limpa o texto
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]  # Limita a 10k caracteres
    except Exception as e:
        print(f"[Erro] Falha ao extrair conteúdo de {url}: {e}")
        return f"Erro ao acessar documentação: {str(e)}"

class Aprendiz:
    def __init__(self, diretorio: str):
        self.diretorio = diretorio
        criar_tabelas()
        print("[Aprendiz] Inicializado.")

    def aprender(self, reset=True):
        if reset:
            limpar_conhecimento()
        total, arquivos, _ = ler_diretorio_aprendizado(self.diretorio)
        print(f"[Aprendiz] Encontrados {total} arquivos.")
        for path, conteudo in arquivos:
            info = extrair_info_arquivo(path, conteudo)
            embedding = gerar_embedding(info["resumo"])
            salvar_conhecimento(path, info["resumo"], info["linguagem"], embedding)
        print(f"[Aprendiz] Index concluído ({total} itens).")
    
    def aprender_com_documentacao_web(self, url: str):
        urls = [url]
        for url in urls:
            print(f"[Aprendiz] Aprendendo de {url}...")
            # extrair conteúdo da documentação
            conteudo = extrair_conteudo_documentacao(url)
            # processar conteúdo
            info = extrair_info_arquivo(url, conteudo)
            # gerar embedding
            embedding = gerar_embedding(info["resumo"])
            # salvar conhecimento
            salvar_conhecimento(url, info["resumo"], info["linguagem"], embedding)
            print(f"[Aprendiz] Aprendido de {url}.")
    
    def aprender_com_diretorio(self, diretorio: str):
        """Aprende com todos os arquivos de um diretório específico."""
        print(f"[Aprendiz] Aprendendo do diretório {diretorio}...")
        
        try:
            total, arquivos, _ = ler_diretorio_aprendizado(diretorio)
            print(f"[Aprendiz] Encontrados {total} arquivos no diretório.")
            
            if total == 0:
                print(f"[Aprendiz] AVISO: Nenhum arquivo suportado encontrado em {diretorio}")
                print(f"[Aprendiz] Extensões suportadas: .py, .js, .jsx, .ts, .tsx, .md, .txt")
                return
            
            for i, (path, conteudo) in enumerate(arquivos, 1):
                print(f"[Aprendiz] Processando arquivo {i}/{total}: {path}")
                try:
                    info = extrair_info_arquivo(path, conteudo)
                    embedding = gerar_embedding(info["resumo"])
                    salvar_conhecimento(path, info["resumo"], info["linguagem"], embedding)
                    print(f"[Aprendiz] ✓ Arquivo processado: {path}")
                except Exception as e:
                    print(f"[Aprendiz] ✗ Erro ao processar {path}: {e}")
            
            print(f"[Aprendiz] Aprendizado do diretório concluído ({total} itens).")
        
        except Exception as e:
            print(f"[Aprendiz] ERRO no aprendizado do diretório: {e}")
            import traceback
            traceback.print_exc()
    
    def aprender_com_arquivo(self, arquivo: str):
        """Aprende com um arquivo específico."""
        print(f"[Aprendiz] Aprendendo do arquivo {arquivo}...")
        try:
            with open(arquivo, "r", encoding="utf-8", errors="ignore") as fp:
                conteudo = fp.read()
            
            info = extrair_info_arquivo(arquivo, conteudo)
            embedding = gerar_embedding(info["resumo"])
            salvar_conhecimento(arquivo, info["resumo"], info["linguagem"], embedding)
            
            print(f"[Aprendiz] Arquivo {arquivo} aprendido com sucesso.")
        except Exception as e:
            print(f"[Erro] Falha ao processar arquivo {arquivo}: {e}")

    def buscar_contexto_relevante(self, pergunta: str, limite=10):
        emb = gerar_embedding(pergunta)
        pares = buscar_por_embedding(emb, limite=limite)
        return pares

    def consultar(self, pergunta: str):
        contexto = self.buscar_contexto_relevante(pergunta, limite=12)
        return perguntar_a_llm(pergunta, contexto)

    def debug_listar_sample(self, n=5):
        return obter_conhecimento(n)
