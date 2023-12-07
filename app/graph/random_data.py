
from flask import current_app
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os 
from typing import Tuple, Dict, Any, List
import csv
from .models import DataControl

    
def get_minY_maxY(data:List[Dict[str, Any]], headers:List[str]) -> Tuple[float, float]:
    result = []

    # Iterate through each dictionary in the data
    for entry in data:
        for key in headers:
            # Check if the key is present and not None
            if key in entry and entry[key] is not None:
                # Assuming the key contains numeric data
                result.append(float(entry[key]))

    # Calculate min and max values
    min_value = min(result)
    max_value = max(result)

    return min_value, max_value


def create_random_test_data() -> Dict[str, Any]:
    

    # 2022년 1월 1일부터 12월 31일까지의 날짜 생성
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2022, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')  # MS: Month Start

    # 날짜에 해당하는 문자열로 변환하여 labels 업데이트
    labels = [date.strftime('%Y-%m-%d') for date in date_range]
    # 랜덤한 값 생성 (여기서는 예시로 랜덤 값 생성)
    
    
    num_values = len(labels)

    num_median = 30
    values = [num_median]*num_values
    
    for _ in range(10):
        num_random = np.sqrt(np.random.randint(1, 100))
        values = [ (value + np.random.randint(-num_random, num_random)) for value in values]
    
    limit = {}
    limit["up"] = [60]*num_values
    limit["down"] = [0]*num_values
    
    data = {
    'labels': labels,
    'values': values
    }
    
    dc = DataControl("data1")
    dc.delete_data_except_header()
    dc.save_data(data, limit)
    
    data_ = dc.read_data()
    
    return data_



