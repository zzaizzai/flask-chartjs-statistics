from flask import render_template, current_app, jsonify, request, redirect
from . import api_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta
from app.graph.models import DataControl
from app.graph.random_data import create_random_test_data

@api_bp.route('/')
def tasks_page():

    return "graph page"

@api_bp.route('/test')
def test():
    
    context={'test': 'test'}
    
    return jsonify(context)

@api_bp.route('/graph/create/parts', methods=['POST'])
def create_parts():
    
    create_random_test_data()
    
    return redirect(request.referrer)
