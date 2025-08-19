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
- Omitir imports necessários"""

def perguntar_a_llm(pergunta, contexto_pairs):
    # contexto_pairs: List[(path, resumo)]
    contexto_fmt = []
    for path, resumo in contexto_pairs[:MAX_ARQUIVOS_CONTEXT]:
        contexto_fmt.append(f"ARQUIVO: {path}\nPADROES:\n{resumo}\n---")
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


def perguntar_a_llm_stream(pergunta, contexto_pairs):
    """Versão com streaming para respostas em tempo real"""
    contexto_fmt = []
    for path, resumo in contexto_pairs[:MAX_ARQUIVOS_CONTEXT]:
        contexto_fmt.append(f"ARQUIVO: {path}\nPADROES:\n{resumo}\n---")
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