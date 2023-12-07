from flask import render_template, current_app, jsonify
from . import api_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta

@api_bp.route('/')
def tasks_page():

    return "graph page"

@api_bp.route('/test')
def test():
    
    context={'test': 'test'}
    
    return jsonify(context)
