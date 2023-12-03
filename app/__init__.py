from flask import Flask, jsonify, request, render_template, Blueprint, redirect
from app.graph import graph_bp

# from app.graph import 

app = Flask(__name__)
app.register_blueprint(graph_bp, url_prefix="/graph")
app.config.from_pyfile('settings.py')


@app.route("/")
def default():
    return redirect('/index')

    
@app.route('/index')
def index():
    return render_template('index.html')