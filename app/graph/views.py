from flask import render_template, current_app
from . import graph_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta
from .random_data import create_random_test_data, get_minY_maxY
@graph_bp.route('/')
def tasks_page():

    return "graph page"

@graph_bp.route('/test')
def test():
    
    #  random data
    data  = create_random_test_data()
    
    # convert to json
    chart_data  = json.dumps(data)
    
    minY, maxY = get_minY_maxY(data, ["value", 'limit_up', 'limit_down'])

    context = {
        'chart_data': chart_data,
        'maxY': maxY,
        'minY': minY
    }
    
    return render_template('test.html', **context)
