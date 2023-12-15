import json
from datetime import datetime, timedelta

from flask import render_template, current_app, request

from . import graph_bp 
from .random_data import get_minY_maxY
from .models import AnalysisData, DataControl

from dateutil.relativedelta import relativedelta


@graph_bp.route('/')
def tasks_page():

    return "graph page"


@graph_bp.route('/show_parts')
def show_parts():
    span = request.args.get('span', default=None, type=str)   

    date_start = request.args.get('date_start', default=None, type=str)
    date_end = request.args.get('date_end', default=None, type=str)
    
    if span is None:
        if date_start is None or date_end is None:
            span = "12m"
    
    # Check span
    if span is not None:
        span_value = int(span[:-1])
        if span[-1] == 'm':
            today = datetime.today()
            date_start = (today - relativedelta(months=span_value)).strftime("%Y-%m-%d")
            date_end = today.strftime("%Y-%m-%d")
    
    
    dc = DataControl('data1')
    part_no_list = dc.get_all_unique_part_no()
    
    context = {}
    context['part_no_list'] = part_no_list
    context['date_start'] = date_start
    context['date_end'] = date_end
    
    return render_template('part_list.html', **context)



@graph_bp.route('/show_part_detail')
def show_part_detail():
    
    date_start = request.args.get('date_start', default=None, type=str)
    date_end = request.args.get('date_end', default=None, type=str)
    
    dc = DataControl('data1', date_start=date_start, date_end=date_end)
    
    
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
        'date_start' : date_start,
        'date_end' : date_end,
        'part_no' : part_no,
        'chart_data': chart_data_json,
        'maxY': maxY,
        'minY': minY,
        'displayMin': display_min,
        'displayMax': display_max,
        'analysis_data':analysis_data
    }
    
    return render_template('test.html', **context)
