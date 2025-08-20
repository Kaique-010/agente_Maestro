import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from config import OPENAI_API_KEY, LLM_MODEL, MAX_ARQUIVOS_CONTEXT
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT_SISTEMA = """Você é um desenvolvedor sênior especialista em Django (DRF) e React Native.
Gere código seguindo EXATAMENTE os padrões do contexto: nomes, organização, imports e bibliotecas.
Não invente libs. Mantenha o estilo consistente com o projeto de referência.
Responda com trechos de código completos e explicação curta quando necessário.

REGRAS DE FORMATAÇÃO DE CÓDIGO:
- SEMPRE preserve indentação correta e estrutura hierárquica
- Para Python: use 4 espaços para indentação (PEP8)
- Para JavaScript/React Native: use 2 espaços para indentação
- Para HTML/CSS: use 2 espaços para indentação
- NUNCA use código inline para blocos multi-linha
- Sempre use blocos de código markdown com linguagem especificada
- Mantenha quebras de linha e espaçamento original
- Para código complexo, sempre use formatação em bloco

FORMATAÇÃO DE RESPOSTA:
- Use ```linguagem para blocos de código
- Preserve espaços em branco e indentação
- Separe explicações do código claramente
- Para código React Native, inclua imports necessários
- Para Django, inclua imports e estrutura de classes/funções

EXEMPLO CORRETO:
```python
def exemplo_funcao():
    if condicao:
        for item in lista:
            if item.valido:
                processar(item)
                print(f"Processado: {item}")
                
    return resultado
```

```javascript
const FormPedidoVenda = () => {
  const [dados, setDados] = useState({
    cliente: '',
    vendedor: '',
    produtos: []
  });
  
  const handleSubmit = () => {
    // lógica de envio
  };
  
  return (
    <View style={styles.container}>
      <Text>Formulário</Text>
    </View>
  );
};
```

EVITE:
- Código inline para blocos complexos
- Perda de indentação
- Misturar explicação com código
- Omitir imports necessários

USO DE FERRAMENTAS:
- Se a pergunta do usuário exigir informações que não estão no contexto (por exemplo, sobre uma biblioteca que não foi usada ainda, ou um conceito novo), você DEVE usar a ferramenta de busca na web.
- Para usar a busca, responda APENAS com o seguinte formato: [pesquisar: 'sua query aqui']
- A query deve ser uma string concisa e direta.
- A função retornará um resumo dos resultados que você pode usar para formular sua resposta."""

import re

def executar_pergunta_com_ferramentas(pergunta, contexto_pairs, stream=False):
    """Orquestra a execução de perguntas, permitindo o uso de ferramentas como a pesquisa na web."""
    if stream:
        stream_original = _perguntar_a_llm_stream_direto(pergunta, contexto_pairs)
        # Como o streaming complica a detecção de chamadas de ferramentas, 
        # por enquanto, vamos passar a resposta diretamente.
        # Uma implementação futura poderia bufferizar a resposta inicial.
        return stream_original

    resposta_inicial = _perguntar_a_llm_direto(pergunta, contexto_pairs)

    # Padrão para detectar: [pesquisar: 'termo de busca']
    padrao_pesquisa = r"\\[pesquisar: '(.*?)'\\]"
    match = re.search(padrao_pesquisa, resposta_inicial)

    if match:
        query = match.group(1)
        print(f"\n[INFO] Detectada chamada de ferramenta: pesquisar_na_web('{query}')")
        resultados_pesquisa = pesquisar_na_web(query)

        # Novo prompt para a LLM com os resultados da pesquisa
        # Registrar a fonte antes de retornar a resposta
        registrar_fonte(f"pesquisar: '{query}'", resultados_pesquisa, 'web')

        novo_contexto = f"""Resultados da pesquisa para '{query}':
{resultados_pesquisa}

Com base nos resultados acima, responda à pergunta original: {pergunta}"""
        
        # Remove o contexto de arquivos para focar nos resultados da web
        return _perguntar_a_llm_direto(novo_contexto, [])
    
    return resposta_inicial

def _carregar_conteudo_arquivo(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fp:
            return fp.read()
    except Exception as e:
        print(f"[Erro] Falha ao ler o arquivo {path}: {e}")
        return None

def _perguntar_a_llm_direto(pergunta, contexto_pairs):
    contexto_fmt = []
    for path, resumo in contexto_pairs[:MAX_ARQUIVOS_CONTEXT]:
        conteudo = _carregar_conteudo_arquivo(path)
        if conteudo:
            contexto_fmt.append(f"ARQUIVO: {path}\nCONTEUDO:\n```\n{conteudo}\n```\n---")
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


def _perguntar_a_llm_stream_direto(pergunta, contexto_pairs):
    """Versão com streaming para respostas em tempo real"""
    contexto_fmt = []
    for path, resumo in contexto_pairs[:MAX_ARQUIVOS_CONTEXT]:
        conteudo = _carregar_conteudo_arquivo(path)
        if conteudo:
            contexto_fmt.append(f"ARQUIVO: {path}\nCONTEUDO:\n```\n{conteudo}\n```\n---")
    contexto_txt = "\n".join(contexto_fmt)

    mensagens = [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": f"Contexto de referência:\n{contexto_txt}\n\nPergunta:\n{pergunta}"}
    ]
    
    return client.chat.completions.create(
        model=LLM_MODEL,
        messages=mensagens,
        temperature=0,
        stream=True
    )

def pesquisar_na_web(query: str, num_results: int = 5) -> str:
    """Realiza uma busca na web e retorna um resumo dos resultados."""
    search_url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        results = soup.find_all('div', class_='result')
        
        resumo_final = ""
        for i, result in enumerate(results[:num_results]):
            title_element = result.find('a', class_='result__a')
            snippet_element = result.find('a', class_='result__snippet')
            link_element = result.find('a', class_='result__url')
            
            if title_element and snippet_element and link_element:
                title = title_element.get_text(strip=True)
                snippet = snippet_element.get_text(strip=True)
                link = link_element.get_text(strip=True)
                resumo_final += f"### {title}\n**Link:** {link}\n**Resumo:** {snippet}\n\n"
        
        return resumo_final if resumo_final else "Nenhum resultado encontrado."

    except requests.RequestException as e:
        return f"Erro ao pesquisar na web: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"