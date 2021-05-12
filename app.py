from flask import Flask, render_template

#Create a Flask app named after this file
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data=[{
        'description': 'Render dummy data',
        'complete': True
    }, {
        'description': 'Set up database',
        'complete': False
    }, {
        'description': 'Set up UX framework',
        'complete': False
    }])