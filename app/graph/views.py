from flask import render_template, current_app, request
from . import graph_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta
from .random_data import create_random_test_data, get_minY_maxY
from .models import AnalysisData, DataControl



@graph_bp.route('/')
def tasks_page():

    return "graph page"

@graph_bp.route('/test')
def test():
    
    dc = DataControl('data1')
    
    display_min = request.args.get('min', default=None, type=int)
    display_max = request.args.get('max', default=None, type=int)
    part_no = request.args.get('part_no', default=None, type=str)

    if part_no is None:
        part_no = 'A10'

    chart_data  = dc.read_data(part_no=part_no)
    
    if len(chart_data) == 0 :
        return render_template('test.html')
    # convert to json
    chart_data_json  = json.dumps(chart_data)
    
    minY, maxY = get_minY_maxY(chart_data, ["value", 'limit_up', 'limit_down'])

    ad  = AnalysisData(chart_data=chart_data)
    analysis_data =  ad.calculate_analysis_data()
    context = {
        'part_no' : part_no,
        'chart_data': chart_data_json,
        'maxY': maxY,
        'minY': minY,
        'displayMin': display_min,
        'displayMax': display_max,
        'analysis_data':analysis_data
    }
    
    return render_template('test.html', **context)
