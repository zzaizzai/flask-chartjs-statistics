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
    data  = create_random_test_data()
    # 데이터를 JSON 형식으로 변환하여 템플릿으로 전달
    chart_data = json.dumps(data)
    # print(chart_data)
    minY, maxY = get_minY_maxY(data, ["value", 'limit_up', 'limit_down'])

    
    return render_template('test.html', chart_data=chart_data, maxY=maxY, minY=minY)
