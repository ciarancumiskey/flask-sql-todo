from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

#Create a Flask app named after this file, then set up the DB connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://todo:todo@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#Create the model, then instantiate it
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    complete = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Todo #{self.id}: {self.description}>'

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    todo_body = {}
    try:
        #Get the data from the user's POST request
        description = request.get_json()['description']
        todo_complete = request.get_json()['complete']
        #Use that POSTed data to create a Todo object
        new_todo = Todo(description=description, complete=bool(todo_complete))
        db.session.add(new_todo)
        db.session.commit()
        todo_body['description'] = new_todo.description
        todo_body['complete'] = new_todo.complete
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    if not error:
        #Instead of returning the user to the index page, return the JSON data to the client
        return jsonify(todo_body)
    
    