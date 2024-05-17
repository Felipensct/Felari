from flask import Flask,render_template,url_for,request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
 

app = Flask(__name__)
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

@app.route('/', methods=['POST','GET'])
def index():
    if request.method=='POST':
        task_content = request.form['content']
        new_task = aFazer(content = task_content)
        

        try:
            db.session.add(new_task)
            db.session.commit()
            new_task.serial_number = f'AF-{new_task.id}'
            db.session.commit()
            return redirect('/')
        except:
            return 'Houve um erro'
    else:
        tasks = aFazer.query.order_by(aFazer.date_created).all()
        return render_template('index.html', tasks = tasks)
    

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = aFazer.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um erro'
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = aFazer.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Houve um erro ao atualizar a tarefa'

    else:
        return render_template('update.html', task=task)
    

if __name__ == '__main__':
    app.run(debug=True, port='5001')