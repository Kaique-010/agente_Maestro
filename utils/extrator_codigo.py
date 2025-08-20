import re
from pathlib import Path

EXTS_CODE = {".py", ".js", ".jsx", ".ts", ".tsx"}
EXTS_TEXT = {".md", ".txt", ".pdf"}

def eh_arquivo_suportado(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return ext in EXTS_CODE or ext in EXTS_TEXT

def linguagem_por_ext(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".py": return "python"
    if ext in [".js", ".jsx"]: return "javascript"
    if ext in [".ts", ".tsx"]: return "typescript"
    if ext in EXTS_TEXT: return "texto"
    return "outro"

def extrair_info_arquivo(path, conteudo, limite_chars=2000):
    lang = linguagem_por_ext(path)
    resumo = []

    if lang == "python":
        classes = re.findall(r"^class\s+[\w_]+", conteudo, re.M)
        funcoes = re.findall(r"^def\s+[\w_]+", conteudo, re.M)
        imports = re.findall(r"^(?:from\s+\S+\s+import\s+\S+|import\s+\S+)", conteudo, re.M)
        # Sinais de Django
        sinais = []
        if re.search(r"from\s+rest_framework", conteudo): sinais.append("DRF")
        if re.search(r"serializers\.ModelSerializer", conteudo): sinais.append("Serializer")
        if re.search(r"ViewSet|APIView|GenericViewSet", conteudo): sinais.append("Views")
        if re.search(r"urlpatterns\s*=", conteudo): sinais.append("URLs")

        resumo += [
            f"language=python",
            f"classes={classes[:30]}",
            f"functions={funcoes[:50]}",
            f"imports={imports[:50]}",
            f"framework_signals={sinais}",
        ]

    elif lang in ["javascript", "typescript"]:
        comp = re.findall(r"(?:function\s+[\w_]+|const\s+[\w_]+\s*=\s*\()", conteudo)
        hooks = re.findall(r"\buse[A-Z]\w+", conteudo)
        imports = re.findall(r"^import\s+.*\s+from\s+['\"].+['\"]", conteudo, re.M)
        rn_sinais = []
        if re.search(r"from\s+'react-native'|from\s+\"react-native\"", conteudo): rn_sinais.append("ReactNative")
        if re.search(r"@react-navigation|createStackNavigator", conteudo): rn_sinais.append("Navigation")
        resumo += [
            f"language={lang}",
            f"components={comp[:50]}",
            f"hooks={hooks[:50]}",
            f"imports={imports[:50]}",
            f"framework_signals={rn_sinais}",
        ]

    else:
        # README / textos ajudam a capturar convenções
        linhas = [l.strip() for l in conteudo.splitlines() if l.strip()][:60]
        resumo += [f"language={lang}", "headlines=" + " | ".join(linhas[:20])]

    # Recorte para não explodir tokens
    corpo_amostra = conteudo[:limite_chars]
    resumo.append("snippet=" + corpo_amostra.replace("\n", " ")[:limite_chars])

    return {
        "linguagem": lang,
        "resumo": "\n".join(resumo)
    }
