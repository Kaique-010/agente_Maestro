import os
import PyPDF2
from utils.extrator_codigo import eh_arquivo_suportado

def ler_pdf(caminho_arquivo: str):
    try:
        with open(caminho_arquivo, 'rb') as f:
            leitor = PyPDF2.PdfReader(f)
            texto = ''
            for pagina in leitor.pages:
                texto += pagina.extract_text()
            return texto
    except Exception as e:
        print(f"Erro ao ler o arquivo PDF {caminho_arquivo}: {e}")
        return None

def ler_diretorio_aprendizado(diretorio_base: str):
    arquivos = []
    json_files = []
    readme_files = []
    total = 0

    for root, _, files in os.walk(diretorio_base):
        for f in files:
            path = os.path.join(root, f)
            if path.lower().endswith('.pdf'):
                conteudo = ler_pdf(path)
                if conteudo is None:
                    continue
            elif eh_arquivo_suportado(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                        conteudo = fp.read()
                except Exception:
                    continue
            else:
                continue
            total += 1
            arquivos.append((path, conteudo))
            if f.lower().endswith(".json"):
                json_files.append(path)
            if f.lower().startswith("readme"):
                readme_files.append(path)

    return total, arquivos, readme_files
