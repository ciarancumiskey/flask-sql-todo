from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

#Create a Flask app named after this file, then set up the DB connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://todo:$PASSWORDGOESHERE@localhost:5432/todoapp'
db = SQLAlchemy(app)

#Create the model, then instantiate it
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo #{self.id}: {self.description}>'

db.create_all()

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())

@app.route('/create-todo', methods=['POST'])
def create_todo():
    description = request.form.get('description', '')
    todo_complete = request.form.get('complete', False)
    new_todo = Todo(description=description, complete=bool(todo_complete))
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))
    #return render_template('add_todo.html')