import json
from datetime import datetime, timedelta

from flask import render_template, current_app, request, flash

from . import graph_bp 
from .random_data import get_minY_maxY
from .models import AnalysisData, PartDataControl, ProductDataControl, ProductChildDataControl

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
    
    
    try:
        dc = PartDataControl()
        part_no_list = dc.get_all_unique_no()

        context = {
            'part_no_list': part_no_list,
            'date_start': date_start,
            'date_end' : date_end
            
        }
    except Exception as e:
        flash(e, 'error')
        
    return render_template('part_list.html', **context)



@graph_bp.route('/show_part_detail')
def show_part_detail():
    
    date_start = request.args.get('date_start', default=None, type=str)
    date_end = request.args.get('date_end', default=None, type=str)
    
    dc = PartDataControl()
    
    
    display_min = request.args.get('min', default=None, type=int)
    display_max = request.args.get('max', default=None, type=int)
    part_no = request.args.get('part_no', default=None, type=str)

    if part_no is None:
        part_no = 'A10'

    if date_start is None and date_end is None:
        today = datetime.today()
        date_start = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
        date_end = today.strftime("%Y-%m-%d")

    chart_data  = dc.get_data_with_part_no(part_no=part_no, date_start=date_start, date_end=date_end)


    if len(chart_data) == 0 :
        return render_template('part_detail.html')
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
    
    return render_template('part_detail.html', **context)


@graph_bp.route('/show_product_detail')
def show_product_detail():
    
    product_no = request.args.get('product_no', default='PRODUCT-AC010', type=str)
    date_start = request.args.get('date_start', default=None, type=str)
    date_end = request.args.get('date_end', default=None, type=str)
    
    if date_start is None and date_end is None:
        today = datetime.today()
        date_start = (today - relativedelta(months=12)).strftime("%Y-%m-%d")
        date_end = today.strftime("%Y-%m-%d")
    
    # get parts of product
    
    product_child_data_control = ProductChildDataControl()
    child_part_no_list = product_child_data_control.get_child_data_part_no_list(product_no)
    context = {
        'product_no': product_no,
        'part_no_list' : child_part_no_list,
        'date_end' : date_end,
        'date_start' : date_start,
        }
    return render_template('product_detail.html', **context)


@graph_bp.route('/show_product_list')
def show_product_list():
    
    dc = ProductDataControl()
    product_no_list = dc.get_all_unique_no()
    
    context = {
        'product_no_list': product_no_list
        }
    return render_template('product_list.html', **context)