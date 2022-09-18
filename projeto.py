from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel

# Instanciando FastAPI
app = FastAPI()

# Algumas constantes úteis
OK = 'OK'
FALHA = 'FALHA'

# Classe representando os dados de endereço do cliente
class Endereco(BaseModel):
    rua: str
    cep: str
    cidade: str
    estado: str
    
# Classe representando os dados do cliente
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str
    
# Classe representadno a lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Optional[Usuario]
    enderecos: List[Endereco] = []
    
# Classe representando os dados do produto
class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    
# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):
    id_usuario: Optional[int]
    produtos: List[Produto] = []
    preco_total: float = 0.0
    quantidade_de_produtos: int = 0
    
    def adiciona_produto(self, produto: Produto):
        self.produtos.append(produto)
        self.preco_total += produto.preco
        self.quantidade_de_produtos += 1
        
    def remove_produto(self, id_produto: int):
        self.preco_total -= db_produtos[id_produto].preco
        self.quantidade_de_produtos -= 1
        self.produtos.remove(db_produtos[id_produto])
    
# Persistência de dados (bancos)
db_usuarios = {}
db_produtos = {}
db_enderecos = {}
db_carrinhos = {}

# Rotas da API
# Cria um usuário
@app.post('/usuario')
async def criar_usuario(usuario: Usuario):
    # Validação do ID
    if usuario.id in db_usuarios:
        return FALHA
    
    # Validação do e-mail
    if '@' not in usuario.email:
        return FALHA
    
    # Validação da senha
    if len(usuario.senha) < 3:
        return FALHA
    
    # Adiciona usuário ao banco
    db_usuarios[usuario.id] = usuario
    return OK

# Retorna um usuário pelo id ou nome
@app.get('/usuario/{id_usuario}')
async def retornar_usuario(id_usuario: int | str):
    if type(id_usuario) == int:
        if id_usuario in db_usuarios:
            return db_usuarios[id_usuario]
    else:
        for usuario in db_usuarios.values():
            if usuario.nome == id_usuario:
                return usuario
        
    return FALHA

# Remover usuário
@app.delete('/usuario/{id_usuario}')
async def deletar_usuario(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    
    if id_usuario in db_enderecos:
        db_enderecos.pop(id_usuario)
        
    if id_usuario in db_carrinhos:
        db_carrinhos.pop(id_usuario)
    
    db_usuarios.pop(id_usuario)
    
    return OK

# Criar endereço do usuário
@app.post('/usuario/{id_usuario}/endereco')
async def criar_endereco(id_usuario: int, endereco: Endereco):
    if id_usuario not in db_usuarios:
        return FALHA
    
    if id_usuario not in db_enderecos:
        lista_enderecos = ListaDeEnderecosDoUsuario()
        lista_enderecos.usuario = db_usuarios[id_usuario]
        db_enderecos[id_usuario] = lista_enderecos
    
    db_enderecos[id_usuario].enderecos.append(endereco)
    
    return OK

# Retornar endereços do usuário pelo id do usuário
@app.get('/usuario/{id_usuario}/endereco')
async def retornar_enderecos_do_usuario(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    
    if id_usuario not in db_enderecos:
        return list()
    
    return list(db_enderecos[id_usuario])

# Excluir endereço pelo id (índice da lista)
@app.delete('/usuario/{id_usuario}/endereco/{id_endereco}')
async def deletar_endereco(id_usuario: int, id_endereco: int):
    if id_usuario not in db_usuarios:
        return FALHA
    
    if id_usuario not in db_enderecos:
        return FALHA
    
    try:
        if db_enderecos[id_usuario].enderecos[id_endereco]:
            db_enderecos[id_usuario].enderecos.pop(id_endereco)
            return OK
    except:
        return FALHA

# Retornar todos os e-mails que possuem o mesmo domínio
@app.get('/usuario/email/{dominio}')
async def retornar_emails(dominio: str):
    emails = {}
    
    for usuario in db_usuarios.values():
        if usuario.email.split('@')[1] == dominio:
            emails[usuario.id] = usuario.email
    
    if len(emails) > 0:
        return emails
    
    return FALHA

# Criar um produto
@app.post('/produto')
async def criar_produto(produto: Produto):
    if produto.id in db_produtos:
        return FALHA
    db_produtos[produto.id] = produto
    return OK

# Deleta o produto correspondente ao id
@app.delete('/produto/{id_produto}')
async def deletar_produto(id_produto: int):
    if id_produto not in db_produtos:
        return FALHA
    for carrinho in db_carrinhos.values():
        for i in range(0, carrinho.produtos.count(db_produtos[id_produto])):
            carrinho.remove_produto(id_produto)
    db_produtos.pop(id_produto)
    return OK

# Adicionar carrinho ao usuário e adicionar produto ao carrinho
@app.post('/carrinho/{id_usuario}/{id_produto}')
async def adicionar_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos:
        return FALHA
    if id_usuario not in db_carrinhos:
        carrinho = CarrinhoDeCompras()
        carrinho.id_usuario = id_usuario
        db_carrinhos[id_usuario] = carrinho
    db_carrinhos[id_usuario].adiciona_produto(db_produtos[id_produto])
    return OK

# Remover produto do carrinho
@app.delete('/carrinho/{id_usuario}/{id_produto}')
async def remover_produto_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos:
        return FALHA
    db_carrinhos[id_usuario].remove_produto(id_produto)
    return OK

# Retornar carrinho de compras
@app.get('/carrinho/{id_usuario}')
async def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    return db_carrinhos[id_usuario]

# Retornar o número de itens e valor total do carrinho
@app.get('/carrinho/{id_usuario}/totais')
async def retornar_total_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:
        return FALHA
    numero_itens = db_carrinhos[id_usuario].quantidade_de_produtos
    valor_total = db_carrinhos[id_usuario].preco_total
    return numero_itens, valor_total

# Deletar o carrinho correspondente ao id do usuário
@app.delete('/carrinho/{id_usuario}')
async def deletar_carrinho(id_usuario: int):
    if id_usuario not in db_usuarios:
        return FALHA
    db_carrinhos.pop(id_usuario)
    return OK


@app.get('/')
async def bem_vinda():
    site = "Seja bem-vinda"
    return site.replace('\n', '')