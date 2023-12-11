from flask import render_template, current_app, jsonify, request, redirect
from . import api_bp 
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta
from app.graph.models import DataControl, PartData, PartNo
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

@api_bp.route('/graph/get/part', methods=['GET'])
def get_part():
    part_no = request.args.get('part_no', default=None, type=str)
    print(part_no)
    
    dc = DataControl('data1')
    data = dc.get_data_with_part_no(part_no) or None
    
    return jsonify(data)

@api_bp.route('/graph/get/part_color', methods=['GET'])
def get_part_color():
    part_no = request.args.get('part_no', default=None, type=str)
    
    
    pn = PartNo(part_no)
    color = pn.get_color()
    
    data = { 'color' : color }
    
    return jsonify(data)
