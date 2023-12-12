from flask import render_template, current_app, request
from . import graph_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta
from .random_data import get_minY_maxY
from .models import AnalysisData, DataControl



@graph_bp.route('/')
def tasks_page():

    return "graph page"


@graph_bp.route('/tests')
def tests():
    date_start = request.args.get('date_start', default='2022-01-01', type=str)
    date_end = request.args.get('date_end', default='2022-12-31', type=str)
    
    
    dc = DataControl('data1')
    part_no_list = dc.get_all_unique_part_no()
    
    context = {}
    context['part_no_list'] = part_no_list
    context['date_start'] = date_start
    context['date_end'] = date_end
    
    return render_template('part_list.html', **context)



@graph_bp.route('/test')
def test():
    
    dc = DataControl('data1')
    
    display_min = request.args.get('min', default=None, type=int)
    display_max = request.args.get('max', default=None, type=int)
    part_no = request.args.get('part_no', default=None, type=str)

    if part_no is None:
        part_no = 'A10'

    chart_data  = dc.get_data_with_part_no(part_no=part_no)


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
