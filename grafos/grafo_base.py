class No:
    def __init__(self, nome, funcao):
        self.nome = nome
        self.funcao = funcao
        self.id = id(self)
        self.proximos = []
    
    def ligar(self, no):
        self.proximos.append(no)


    def executar(self, estado):
        if self.funcao is not None:
            estado = self.funcao(estado)
        
        for prox in self.proximos:
            estado = prox.executar(estado)  
        return estado
        print('estado:', estado)



