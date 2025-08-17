import os
from utils.extrator_codigo import eh_arquivo_suportado

def ler_diretorio_aprendizado(diretorio_base: str):
    arquivos = []
    json_files = []
    readme_files = []
    total = 0

    for root, _, files in os.walk(diretorio_base):
        for f in files:
            path = os.path.join(root, f)
            if not eh_arquivo_suportado(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    conteudo = fp.read()
            except Exception:
                continue
            total += 1
            arquivos.append((path, conteudo))
            if f.lower().endswith(".json"):
                json_files.append(path)
            if f.lower().startswith("readme"):
                readme_files.append(path)

    return total, arquivos, readme_files
