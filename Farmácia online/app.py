from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave secreta para uso de sessão

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password, pontos=0):
        self.id = id
        self.username = username
        self.password = password
        self.pontos = pontos

users = [
    User(id=1, username='admin', password='admin'),
]

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users if user.id == int(user_id)), None)
# Lista de medicamentos fictícios
lista_de_medicamentos = [
    {'nome': 'Paracetamol', 'preco': '200 Kz', 'imagem': 'paracetamol.jpg', 'avaliacoes': []},
    {'nome': 'Ibuprofeno', 'preco': '300 Kz', 'imagem': 'ibuprofeno.jpg', 'avaliacoes': []},
    {'nome': 'Aspirina', 'preco': '150 Kz', 'imagem': 'aspirina.jpg', 'avaliacoes': []},
    {'nome': 'Cetirizina', 'preco': '250 Kz', 'imagem': 'cetirizina.jpg', 'avaliacoes': []},
    {'nome': 'Loratadina 250mg', 'preco': '270 Kz', 'imagem': 'loratadina.jpg', 'avaliacoes': []},
    {'nome': 'Dipirona', 'preco': '220 Kz', 'imagem': 'dipirona.jpg', 'avaliacoes': []},
    {'nome': 'Omeprazol', 'preco': '310 Kz', 'imagem': 'omeprazol.jpg', 'avaliacoes': []},
    {'nome': 'Ranitidina', 'preco': '300 Kz', 'imagem': 'ranitidina.jpg', 'avaliacoes': []},
    {'nome': 'Clonazepam', 'preco': '400 Kz', 'imagem': 'clonazepam.jpg', 'avaliacoes': []},
    {'nome': 'Diazepam', 'preco': '350 Kz', 'imagem': 'diazepam.jpg', 'avaliacoes': []},
    {'nome': 'Metformina', 'preco': '290 Kz', 'imagem': 'metformina.jpg', 'avaliacoes': []},
    {'nome': 'Glibenclamida', 'preco': '270 Kz', 'imagem': 'glibenclamida.jpg', 'avaliacoes': []},
    {'nome': 'Insulina', 'preco': '450 Kz', 'imagem': 'insulina.jpg', 'avaliacoes': []},
    {'nome': 'Atorvastatina', 'preco': '350 Kz', 'imagem': 'atorvastatina.jpg', 'avaliacoes': []},
    {'nome': 'Sinvastatina', 'preco': '330 Kz', 'imagem': 'sinvastatina.jpg', 'avaliacoes': []},
    {'nome': 'Losartana', 'preco': '300 Kz', 'imagem': 'losartana.jpg', 'avaliacoes': []},
    {'nome': 'Amlodipina', 'preco': '320 Kz', 'imagem': 'amlodipina.jpg', 'avaliacoes': []},
    {'nome': 'Enalapril', 'preco': '310 Kz', 'imagem': 'enalapril.jpg', 'avaliacoes': []},
    {'nome': 'Valsartana', 'preco': '340 Kz', 'imagem': 'valsartana.jpg', 'avaliacoes': []},
]

pedidos = []
@app.route('/')
def home():
    return render_template('home.html', medicamentos=lista_de_medicamentos)

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('query')
    preco_min = request.args.get('preco_min', 0, type=int)
    preco_max = request.args.get('preco_max', float('inf'), type=int)
    categoria = request.args.get('categoria')
    resultados = []
    if query:
        query_lower = query.lower()
        resultados = [medicamento for medicamento in lista_de_medicamentos
                      if query_lower in medicamento['nome'].lower() and
                      preco_min <= int(medicamento['preco'].split()[0]) <= preco_max and
                      (not categoria or medicamento.get('categoria') == categoria)]
    return render_template('buscar.html', resultados=resultados)
@app.route('/carrinho')
def carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []
    return render_template('carrinho.html', carrinho=session['carrinho'])

@app.route('/add_to_cart/<nome>')
def add_to_cart(nome):
    if 'carrinho' not in session:
        session['carrinho'] = []
    for medicamento in lista_de_medicamentos:
        if medicamento['nome'] == nome:
            session['carrinho'].append(medicamento)
            break
    return redirect(url_for('carrinho'))

@app.route('/remove_from_cart/<nome>')
def remove_from_cart(nome):
    if 'carrinho' in session:
        session['carrinho'] = [item for item in session['carrinho'] if item['nome'] != nome]
    return redirect(url_for('carrinho'))
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        total = sum([int(item['preco'].split()[0]) for item in session['carrinho']])
        if current_user.is_authenticated:
            usuario = current_user.username
        else:
            usuario = 'Usuário anônimo'
        pedido = {
            'usuario': usuario,
            'itens': session['carrinho'],
            'total': total,
            'endereco': request.form['endereco']
        }
        pedidos.append(pedido)
        session['carrinho'] = []  # Limpar o carrinho após o checkout
        flash('Pedido realizado com sucesso!')
        if current_user.is_authenticated:
            user = next((u for u in users if u.id == current_user.id), None)
            if user:
                user.pontos += total // 100  # 1 ponto para cada 100 Kz gastos
        return redirect(url_for('historico'))
    else:
        total = sum([int(item['preco'].split()[0]) for item in session['carrinho']])
        return render_template('checkout.html', total=total)
@app.route('/historico')
@login_required
def historico():
    historico_usuario = [pedido for pedido in pedidos if pedido['usuario'] == current_user.username]
    return render_template('historico.html', pedidos=historico_usuario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u.username == username and u.password == password), None)
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha incorretos.')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not any(u.username == username for u in users):
            new_user = User(id=len(users) + 1, username=username, password=password)
            users.append(new_user)
            flash('Registro bem-sucedido! Faça login para continuar.')
            return redirect(url_for('login'))
        else:
            flash('Nome de usuário já existe. Escolha outro.')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route('/perfil')
@login_required
def perfil():
    user = next((u for u in users if u.id == current_user.id), None)
    return render_template('perfil.html', name=current_user.username, pontos=user.pontos)

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')

@app.route('/sugestoes', methods=['GET'])
def sugestoes():
    query = request.args.get('query', '').lower()
    sugestoes = [medicamento['nome'] for medicamento in lista_de_medicamentos if query in medicamento['nome'].lower()]
    return jsonify(sugestoes)
@app.route('/avaliar/<nome>', methods=['POST'])
@login_required
def avaliar(nome):
    avaliacao = request.form['avaliacao']
    for medicamento in lista_de_medicamentos:
        if medicamento['nome'] == nome:
            medicamento['avaliacoes'].append({
                'usuario': current_user.username,
                'avaliacao': avaliacao
            })
    return redirect(url_for('buscar', query=nome))

@app.route('/chatbot', methods=['POST'])
def chatbot():
    mensagem = request.form['mensagem']
    resposta = "Obrigado por entrar em contato! Sua mensagem foi: " + mensagem
    return jsonify({'resposta': resposta})
@app.route('/rastrear_pedido/<int:pedido_id>')
@login_required
def rastrear_pedido(pedido_id):
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        return render_template('rastrear_pedido.html', pedido=pedido)
    else:
        flash('Pedido não encontrado!')
        return redirect(url_for('historico'))

@app.route('/resgatar_pontos', methods=['POST'])
@login_required
def resgatar_pontos():
    user = next((u for u in users if u.id == current_user.id), None)
    if user and user.pontos >= 100:  # exemplo: 100 pontos para 10% de desconto
        desconto = sum([int(item['preco'].split()[0]) for item in session['carrinho']]) * 0.10
        user.pontos -= 100
        flash(f'Desconto de {desconto} Kz aplicado! Você tem {user.pontos} pontos restantes.')
    else:
        flash('Pontos insuficientes para resgate.')
    return redirect(url_for('carrinho'))

@app.route('/admin')
@login_required
def admin():
    if current_user.username == 'admin':
        return render_template('edicao.html')
    else:
        flash('Acesso negado!')
        return redirect(url_for('home'))

@app.route('/editar', methods=['POST'])
@login_required
def editar():
    if current_user.username == 'admin':
        # Adicione lógica de edição aqui
        flash('Edição realizada com sucesso!')
        return redirect(url_for('admin'))
    else:
        flash('Acesso negado!')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
