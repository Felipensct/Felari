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



# Simulando um banco de dados
produtos = []

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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = aFazer(content=form.content.data)
        new_task.serial_number = str(random.randint(100000, 999999))
        db.session.add(new_task)
        db.session.commit()
        flash('Produto adicionado com sucesso!')
        return redirect('/')
    tasks = aFazer.query.order_by(aFazer.date_created).all()
    return render_template('index.html', form=form, tasks=tasks)


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
    form = TaskForm()
    if form.validate_on_submit():
        new_task = aFazer(content=form.content.data)
        new_task.serial_number = str(random.randint(100000, 999999))
        db.session.add(new_task)
        db.session.commit()
        flash('Produto adicionado com sucesso!')
        return redirect('/')
    tasks = aFazer.query.order_by(aFazer.date_created).all()
    return render_template('nextOrders.html', form=form, tasks=tasks)


@app.route('/products')
def products():
    return render_template('products.html', produtos=produtos)

@app.route('/create_product', methods=['POST'])
def create_product():
    nome_produto = request.form.get('nomeProduto')
    ultima_producao = request.form.get('ultimoProducao')
    roteiro = request.form.get('roteiro')

    novo_produto = {
        'nome': nome_produto,
        'ultima_producao': datetime.strptime(ultima_producao, '%Y-%m-%d').strftime('%d/%m/%y'),
        'roteiro': roteiro
    }

    produtos.append(novo_produto)
    flash('Produto adicionado com sucesso!')

    return redirect(url_for('products'))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = aFazer.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash('Produto deletado com sucesso!')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port='5001')
