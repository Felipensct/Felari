import random
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SECRET_KEY'] = 'root'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def create_user(username):
        default_password = 'password'  # Senha padrão
        hashed_password = generate_password_hash(default_password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

class AccessPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class AccessPointForm(FlaskForm):
    name = StringField('Nome do Ponto de Acesso', validators=[DataRequired()])
    submit = SubmitField('Criar Ponto de Acesso')

products_access_points = db.Table('products_access_points',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('access_point_id', db.Integer, db.ForeignKey('access_point.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ultima_producao = db.Column(db.DateTime)
    access_points = db.relationship('AccessPoint', secondary=products_access_points, backref=db.backref('products', lazy='dynamic'))

class OrdemProducao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    produto = db.relationship('Product', backref=db.backref('ordens_producao', lazy=True))
    quantidade = db.Column(db.Integer, nullable=False)
    data_prevista = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<OrdemProducao {self.id}>'

class Serial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True)
    ordem_id = db.Column(db.Integer, db.ForeignKey('ordem_producao.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ordem = db.relationship('OrdemProducao', backref=db.backref('seriais', lazy=True))

class aFazer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True)
    content = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class TaskForm(FlaskForm):
    content = StringField(validators=[DataRequired(), Length(min=5, max=200)])
    submit = SubmitField('Atualizar')

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=5, max=150)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=5, max=150)])
    submit = SubmitField('Registrar')

class TraceSerial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(50), nullable=False)
    date_done = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    access_point = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<TraceSerial {self.serial}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    produtos = Product.query.join(Product.access_points).all()
    ordens = OrdemProducao.query.order_by(OrdemProducao.data_prevista).all()
    form = TaskForm()
    if form.validate_on_submit():
        new_task = aFazer(content=form.content.data)
        new_task.serial_number = str(random.randint(100000, 999999))
        db.session.add(new_task)
        db.session.commit()
        flash('Produto adicionado com sucesso!')
        return redirect('/')
    
    tasks = aFazer.query.order_by(aFazer.date_created).all()
    access_points = AccessPoint.query.all()
    return render_template('index.html', form=form, tasks=tasks, access_points=access_points, produtos=produtos, ordens=ordens)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!')
    return redirect(url_for('login'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = aFazer.query.get_or_404(id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.content = form.content.data
        db.session.commit()
        return redirect('/')
    return render_template('update.html', form=form, task=task)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login bem-sucedido!')
            return redirect(url_for('index'))
        else:
            flash('Login inválido. Verifique seu usuário e senha.')
    return render_template('login.html', form=form, loginPage=True)

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro bem-sucedido!')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/pastProductions', methods=['GET', 'POST'])
@login_required
def pastProductions():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = aFazer(content=form.content.data)
        new_task.serial_number = str(random.randint(100000, 999999))
        db.session.add(new_task)
        db.session.commit()
        flash('Produto adicionado com sucesso!')
        return redirect('/')
    tasks = aFazer.query.order_by(aFazer.date_created).all()
    return render_template('pastProductions.html', form=form, tasks=tasks)

@app.route('/nextOrders', methods=['GET', 'POST'])
@login_required
def nextOrders():
    ordens = OrdemProducao.query.order_by(OrdemProducao.data_prevista).all()
    form = TaskForm()
    return render_template('nextOrders.html', ordens=ordens, form=form)

@app.route('/nova_ordem', methods=['POST'])
@login_required
def nova_ordem():
    produto_id = request.form.get('produto_id')
    quantidade = request.form.get('quantidade')
    data_prevista_str = request.form.get('data_prevista')

    if not produto_id or not quantidade or not data_prevista_str:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('index'))

    try:
        data_hora_prevista = datetime.fromisoformat(data_prevista_str)
    except ValueError:
        flash('Formato de data e hora inválido. Use o formato YYYY-MM-DDTHH:MM.', 'error')
        return redirect(url_for('index'))

    nova_ordem = OrdemProducao(produto_id=produto_id, quantidade=quantidade, data_prevista=data_hora_prevista)
    db.session.add(nova_ordem)
    db.session.commit()
    flash('Ordem de produção criada com sucesso!')
    return redirect(url_for('index'))

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    form = TaskForm()
    produtos = Product.query.all()
    access_points = AccessPoint.query.all()

    if request.method == 'POST':
        produto_nome = request.form['nome']
        roteiro_id = int(request.form['roteiro'])

        produto = Product.query.filter_by(nome=produto_nome).first()
        if produto:
            access_point = AccessPoint.query.get(roteiro_id)
            if access_point:
                produto.access_points.append(access_point)
                db.session.commit()
                flash('Roteiro associado ao produto com sucesso!')
            else:
                flash('Roteiro não encontrado.', 'error')
        else:
            flash('Produto não encontrado.', 'error')

        return redirect(url_for('products'))

    return render_template('products.html', produtos=produtos, access_points=access_points, form=form)

@app.route('/create_product', methods=['POST'])
def create_product():
    nome_produto = request.form.get('nome')
    ultima_producao = request.form.get('ultimoProducao')
    roteiros_selecionados = request.form.getlist('roteiros')

    if not nome_produto:
        flash('O nome do produto é obrigatório.', 'error')
        return redirect(url_for('products'))

    produto_existente = Product.query.filter_by(nome=nome_produto).first()
    if produto_existente:
        flash(f'O produto "{nome_produto}" já existe.', 'error')
        return redirect(url_for('products'))

    novo_produto = Product(nome=nome_produto, ultima_producao=datetime.strptime(ultima_producao, '%Y-%m-%d').date() if ultima_producao else None)

    for roteiro_id in roteiros_selecionados:
        access_point = AccessPoint.query.get(roteiro_id)
        if access_point:
            novo_produto.access_points.append(access_point)

    db.session.add(novo_produto)
    db.session.commit()
    flash('Produto adicionado com sucesso!')
    return redirect(url_for('products'))

@app.route('/product/<int:id>', methods=['GET', 'POST'])
@login_required
def product(id):
    produto = Product.query.get_or_404(id)
    access_points = AccessPoint.query.all()
    form = TaskForm(obj=produto)

    if form.validate_on_submit():
        produto.nome = form.nome.data

        if form.ultimoProducao.data:
            produto.ultima_producao = form.ultimoProducao.data
        else:
            produto.ultima_producao = None

        produto.access_points.clear()

        for roteiro_id in request.form.getlist('roteiros'):
            access_point = AccessPoint.query.get(roteiro_id)
            if access_point:
                produto.access_points.append(access_point)

        db.session.commit()
        flash('Produto atualizado com sucesso!')
        return redirect(url_for('index'))

    return render_template('product.html', produto=produto, form=form, access_points=access_points)

@app.route('/update_product/<int:id>', methods=['POST'])
@login_required
def update_product(id):
    produto = Product.query.get_or_404(id)
    form = TaskForm(request.form)

    if form.validate_on_submit():
        produto.nome = form.nome.data

        if form.ultimoProducao.data:
            produto.ultima_producao = form.ultimoProducao.data
        else:
            produto.ultima_producao = None

        produto.access_points.clear()

        for roteiro_id in request.form.getlist('roteiros'):
            access_point = AccessPoint.query.get(roteiro_id)
            if access_point:
                produto.access_points.append(access_point)

        db.session.commit()
        flash('Produto atualizado com sucesso!')
        return redirect(url_for('index'))

    access_points = AccessPoint.query.all()
    return render_template('product.html', produto=produto, form=form, access_points=access_points)

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    produto = Product.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto deletado com sucesso!')
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = aFazer.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash('Produto deletado com sucesso!')
    return redirect('/')

@app.route('/create_access_point', methods=['GET', 'POST'])
def create_access_point():
    form = AccessPointForm()
    if form.validate_on_submit():
        name = form.name.data

        existing_access_point = AccessPoint.query.filter_by(name=name).first()
        if existing_access_point:
            flash('Este ponto de acesso já existe.', 'warning')
            return redirect(url_for('create_access_point'))

        new_access_point = AccessPoint(name=name)
        db.session.add(new_access_point)
        db.session.commit()

        new_user = User.create_user(username=name)

        flash('Ponto de acesso criado com sucesso! Usuário padrão também criado.', 'success')
        return redirect(url_for('create_access_point'))

    return render_template('create_access_point.html', form=form)

@app.route('/generate_serials/<int:ordem_id>', methods=['POST'])
@login_required
def generate_serials(ordem_id):
    ordem = OrdemProducao.query.get_or_404(ordem_id)
    serials = []
    prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    for i in range(ordem.quantidade):
        serial_number = f"{prefix}{ordem_id}-{i + 1:05}"
        novo_serial = Serial(serial_number=serial_number, ordem_id=ordem_id)
        db.session.add(novo_serial)
        serials.append(novo_serial)

        # Atualiza o status da ordem para 2
    ordem.status = 2
    db.session.commit()
    flash('Seriais gerados com sucesso!')
    return redirect('/')

@app.route('/view_serials/<int:ordem_id>', methods=['GET'])
@login_required
def view_serials(ordem_id):
    form = TaskForm()
    ordem = OrdemProducao.query.get_or_404(ordem_id)
    seriais = Serial.query.filter_by(ordem_id=ordem_id).all()
    return render_template('view_serials.html', ordem=ordem, seriais=seriais, form=form)

@app.route('/finalize_production/<int:ordem_id>', methods=['POST'])
@login_required
def finalize_production(ordem_id):
    ordem = OrdemProducao.query.get_or_404(ordem_id)
    ordem.status = 3
    db.session.commit()
    flash('Produção finalizada com sucesso!')
    return redirect(url_for('view_serials', ordem_id=ordem_id))


@app.route('/delete_serials/<int:ordem_id>', methods=['POST'])
@login_required
def delete_serials(ordem_id):
    ordem = OrdemProducao.query.get_or_404(ordem_id)
    seriais = Serial.query.filter_by(ordem_id=ordem_id).all()
    
    if not seriais:
        flash('Não há seriais para deletar.')
        ordem.status = 1
        db.session.commit()
        return redirect('/')
    
    for serial in seriais:
        db.session.delete(serial)
    
    ordem.status = 1
    db.session.commit()
    flash('Todos os seriais foram deletados com sucesso!')
    return redirect('/')

@app.route('/production_page', methods=['GET', 'POST'])
@login_required
def productionPage():
    form = TaskForm()
    ordens = OrdemProducao.query.filter_by(status=2).all()  # Filter orders by status 2
    access_points = AccessPoint.query.all()
    return render_template('production_page.html', ordens=ordens, access_points=access_points, form=form)

@app.route('/process_serial', methods=['POST'])
@login_required
def process_serial():
    produto_id = request.form.get('produtoAtivo')
    serial_number = request.form.get('leituraSerial')

    if not produto_id or not serial_number:
        flash('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('productionPage'))

    trace_serial = TraceSerial(
        serial=serial_number,
        access_point=current_user.username,  # Assuming access point is the current user for this example
        user=current_user.username
    )
    db.session.add(trace_serial)
    db.session.commit()
    flash('Serial processado com sucesso!')
    return redirect(url_for('productionPage'))

@app.route('/trace_serials', methods=['GET'])
@login_required
def showTraceSerial():
    form = TaskForm()
    trace_serials = TraceSerial.query.all()
    return render_template('trace_serials.html', trace_serials=trace_serials, form=form)

@app.route('/delete_all_trace_serials', methods=['POST'])
@login_required
def delete_all_trace_serials():
    db.session.query(TraceSerial).delete()
    db.session.commit()
    flash('Todos os seriais foram deletados com sucesso!')
    return redirect(url_for('showTraceSerial'))

if __name__ == '__main__':
    app.run(debug=True, port='5001')
