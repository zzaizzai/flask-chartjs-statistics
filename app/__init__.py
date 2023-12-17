from flask import Flask, jsonify, request, render_template, Blueprint, redirect, flash
from app.graph import graph_bp
from app.api import api_bp

# from app.graph import 

app = Flask(__name__)
app.config["SECRET_KEY"] = "junsai"
app.static_folder='static'
app.register_blueprint(graph_bp, url_prefix="/graph")
app.register_blueprint(api_bp, url_prefix="/api")
app.config.from_pyfile('settings.py')


@app.route("/")
def default():
    return redirect('/index')

    
@app.route('/index')
def index():
    return render_template('index.html')
