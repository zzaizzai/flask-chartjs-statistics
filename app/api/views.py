import json
from datetime import datetime, timedelta, date

from flask import render_template, current_app, jsonify, request, redirect

from app.graph.models import PartNo, PartDataControl, ProductDataControl, ProductChildDataControl
from . import api_bp 

import numpy as np
import pandas as pd


@api_bp.route('/')
def tasks_page():

    return "graph page"

@api_bp.route('/test')
def test():
    
    context={'test': 'test'}
    
    return jsonify(context)

@api_bp.route('/graph/create/parts', methods=['POST'])
def create_parts():
    
    dc = PartDataControl()
    dc.create_random_test_data()
    
    return redirect(request.referrer)

@api_bp.route('/graph/create/products', methods=['POST'])
def create_products():
    
    dc = ProductDataControl()
    dc.create_random_test_data()
    
    return redirect(request.referrer)


@api_bp.route('/graph/get/part', methods=['GET'])
def get_part():
    part_no = request.args.get('part_no', default=None, type=str)
    print(part_no)
    
    dc = PartDataControl()
    data = dc.get_data_with_part_no(part_no, None, None) or None
    
    return jsonify(data)


@api_bp.route('/graph/get/part_color', methods=['GET'])
def get_part_color():
    
    part_no = request.args.get('part_no', default=None, type=str)
    date_start = request.args.get('date_start', default=None, type=str)
    date_end = request.args.get('date_end', default=None, type=str)

    pn = PartNo(part_no)
    color = pn.get_color(date_start, date_end)
    
    data = { 'color' : color }
    
    return jsonify(data)

@api_bp.route('/graph/create/product_child', methods=['GET'])
def create_product_child():
    aa =  ProductChildDataControl()
    data = aa.get_demo_data()
    
    return jsonify(data)