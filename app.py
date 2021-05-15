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
    priority_level = db.Column(db.String(), nullable=False, default='low')
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo #{self.id}: {self.description}, {self.priority_level} priority>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<List #{self.id}: {self.name}>'

@app.route('/')
def index():
    #Default to showing the 1st Todo list in the database
    return redirect(url_for('get_list_todos', list_id=1))

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    data=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    todo_body = {}
    try:
        #Get the data from the user's POST request
        description = request.get_json()['description']
        priority_level = request.get_json()['priorityLevel']
        #Use that POSTed data to create a Todo object
        new_todo = Todo(description=description, complete=False, priority_level=priority_level)
        db.session.add(new_todo)
        db.session.commit()
        todo_body['description'] = new_todo.description
        todo_body['complete'] = new_todo.complete
        todo_body['priority_level'] = new_todo.priority_level
        todo_body['id'] = new_todo.id
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

#As todo_id is specified in the route, it's available as an argument for the method
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_complete_todo(todo_id):
    try:
        updated_todo = Todo.query.get(todo_id)
        updated_todo.complete = request.get_json()['completed']
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    return jsonify({'success': True})

# @app.route('/lists/create', methods=['POST'])
# def create_todo_list():
#     error = False
#     list_body = {}
#     try:

#     except:

#     finally:
    
#     return