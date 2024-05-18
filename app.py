import random
from flask import Flask,render_template,url_for,request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask import flash

class TaskForm(FlaskForm):
    content = StringField(validators=[DataRequired(), Length(min=5, max=200)])
    submit = SubmitField('Submit')
 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'root'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app,db)



class aFazer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True)
    content = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = aFazer(content=form.content.data)
        new_task.serial_number = str(random.randint(100000, 999999))
        db.session.add(new_task)
        db.session.commit()
        flash('Tarefa adicionada com sucesso!')  # Mensagem flash
        return redirect('/')
    tasks = aFazer.query.order_by(aFazer.date_created).all()
    return render_template('index.html', form=form, tasks=tasks)
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = aFazer.query.get_or_404(id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.content = form.content.data
        db.session.commit()
        return redirect('/')
    return render_template('update.html', form=form, task=task)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = aFazer.query.get_or_404(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash('Tarefa deletada com sucesso!')  # Mensagem flash
    return redirect('/')
    
    

if __name__ == '__main__':
    app.run(debug=True, port='5001')