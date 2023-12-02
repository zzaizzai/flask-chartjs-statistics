from flask import Flask, jsonify, request, render_template, Blueprint, redirect
import numpy as np
import json
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route("/")
def default():
    return redirect('/index')

    
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    
    # 2022년 1월 1일부터 12월 31일까지의 날짜 생성
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='MS')  # MS: Month Start

    # 날짜에 해당하는 문자열로 변환하여 labels 업데이트
    labels = [date.strftime('%B') for date in date_range]
    print(labels)
    # 랜덤한 값 생성 (여기서는 예시로 랜덤 값 생성)
    values = np.random.randint(25, 50, size=(len(labels),)).tolist()
    limit = {}
    limit["up"] = [60]*len(labels)
    limit["down"] = [10]*len(labels)
    data = {
    'labels': labels,
    'values': values
    }

    # 데이터를 JSON 형식으로 변환하여 템플릿으로 전달
    chart_data = json.dumps(data)
    limit_data = json.dumps(limit)
    print(limit_data)
    return render_template('test.html', chart_data=chart_data, limit_data=limit_data)