import os
from banco.conexao import conectar, fechar_conexao

def ler_diretorio_aprendizado(diretorio: str):
    total = 0
    json_files = []
    readme_files = []
    
    conn = conectar()
    for root, dirs, files in os.walk(diretorio):
        for file in files:
            caminho = os.path.join(root, file)
            
            if file.endswith(".json"):
                json_files.append(caminho)
            elif file.endswith(".md"):
                readme_files.append(caminho)
            else:
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO conhecimento (caminho, conteudo) VALUES (?, ?)", 
                                     (caminho, conteudo))
                        conn.commit()
                        total += 1
                except Exception as e:
                    print(f"Error processing file {caminho}: {str(e)}")
                    continue

    fechar_conexao(conn)
    return total, json_files, readme_files
