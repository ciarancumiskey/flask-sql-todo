from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

#Create a Flask app named after this file, then set up the DB connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://todo:todo@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#Create the models, then instantiate them
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    priority_level = db.Column(db.String(), nullable=False, default='low')
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False, 
    default=1)

    def __repr__(self):
        return f'<Todo #{self.id}: {self.description}, {self.priority_level} priority>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<List #{self.id}: {self.name}, todos: {self.todos}>'

@app.route('/')
def index():
    #Default to showing the 1st Todo list in the database
    return redirect(url_for('get_list_todos', list_id=1))

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    todo_body = {}
    try:
        #Get the data from the user's POST request
        description = request.get_json()['description']
        priority_level = request.get_json()['priorityLevel']
        list_id = request.get_json()['listId']
        #Use that POSTed data to create a Todo object
        new_todo = Todo(description=description, complete=False, priority_level=priority_level, list_id=list_id)
        db.session.add(new_todo)
        db.session.commit()
        todo_body['description'] = new_todo.description
        todo_body['complete'] = new_todo.complete
        todo_body['priority_level'] = new_todo.priority_level
        todo_body['id'] = new_todo.id
        todo_body['list_id'] = new_todo.list_id
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

@app.route('/lists/create', methods=['POST'])
def create_todo_list():
    error = False
    list_body = {}
    try:
        new_todolist = TodoList(name=request.get_json()['name'])
        db.session.add(new_todolist)
        db.session.commit()
        list_body['id'] = new_todolist.id
        list_body['name'] = new_todolist.name
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(list_body)

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False
    try:
        doomed_list = TodoList.query.get(list_id)
        #Loop through all of the deleted list's Todos and delete them
        for todo in doomed_list.todos:
            db.session.delete(todo)
        db.session.delete(doomed_list)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({'success': True})


@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_list_complete(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id)
        #Loop through all of this list's Todos and update them
        for todo in list.todos:
            #The checkbox for each list of Todos will only send requests when checked
            todo.complete = True
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return '', 200

if __name__ == '__main__':
    app.run(debug=True)