import csv
import json
import os
from datetime import datetime
from typing import Tuple, Dict, Any, List, Optional

from flask import Flask, current_app

import numpy as np
import pandas as pd

class AnalysisData():
    
    def __init__(self, chart_data: List[Dict[str, Any]]):
        self.chart_data  = chart_data
        
    def calculate_analysis_data(self) -> Dict[str, Any]:
        
        keys =  list(self.chart_data[0].keys())

        data_ave = {}
        for key in keys:
            values = [entry[key] for entry in self.chart_data]
            
            if self.get_average(values) is None:
                continue
            
            data_ave[key] = self.get_average(values)
                
        return data_ave

    def get_average(self, values: List[Any]) -> Optional[float]:
        try:
            average_value = round(sum(values) / len(values), 3)
        except:
            return None
        
        return average_value
    
    
class PartNo():
    
    def __init__(self, part_no: str, date_start = None, date_end = None):
        self.part_no = part_no
        
        self.data_control = DataControl('data1')
        self.date_start = date_start if date_start is not None else '2022-01-01'
        self.date_start = date_end if date_end is not None else '2022-12-31'
        
        
    def get_color(self, date_start = None, date_end = None):
        part_no_data = self.data_control.get_data_with_part_no(self.part_no)
        
        date_start = datetime.strptime(date_start, "%Y-%m-%d") if date_start else datetime(2022, 1, 1)
        date_end = datetime.strptime(date_end, "%Y-%m-%d") if date_end else datetime(2022, 12, 31)
        
        num_items = 0
        num_error = 0
        
        for data_part in part_no_data:
            data_date = datetime.strptime(data_part['datetime'], "%Y-%m-%d")  # 데이터의 날짜를 datetime 객체로 변환
            if (not date_start or data_date >= date_start) and (not date_end or data_date <= date_end):
                num_items += 1
                if data_part['value'] > data_part['limit_up']:
                    num_error += 1
                
                if data_part['value'] < data_part['limit_down']:
                    num_error += 1
                
        if num_items == 0:
            return 'gray'

        if num_error > (len(part_no_data)/100):
            return 'red'
        
        if num_error > (len(part_no_data)/500):
            return 'orange'
        

        return 'blue'

class PartData():
    
    def __init__(self, **kwrrg):
        self.datetime = kwrrg['datetime']
        self.lot = kwrrg['lot']
        self.limit_down = kwrrg['limit_down']
        self.limit_up = kwrrg['limit_up']
        self.part_no = kwrrg['part_no']
        self.value = kwrrg['value']
        
    def to_dict(self):
        return {
            'datetime': self.datetime,
            'lot': self.lot,
            'limit_down': self.limit_down,
            'limit_up': self.limit_up,
            'part_no': self.part_no,
            'value': self.value
        }
        
class DataControl():
    
    
    def __init__(self, data_name: str, date_start = None, date_end = None):
        
        self.data_name = data_name
        self.save_dir = current_app.config["SAVE_DIR"]
        self.file_path = os.path.join(self.save_dir, f"{data_name}.csv")
        self.date_start = date_start if date_start is not None else '2022-01-01'
        self.date_start = date_end if date_end is not None else '2022-12-31'
        
    def delete_data_except_header(self) -> None:

        header = ["lot", "datetime", "value", "limit_up", "limit_down", "part_no"]

        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            
    def get_all_unique_part_no(self) -> List[str]:
        
        if not os.path.exists(self.file_path):
            return []
        # You may optionally read the content you just wrote
        with open(self.file_path, "r") as f:
            csv_reader = csv.DictReader(f)

            # Use a set to store unique part_no values
            unique_part_nos = set()

            for row in csv_reader:
                part_no_value = row.get('part_no')
                if part_no_value not in unique_part_nos:
                    unique_part_nos.add(part_no_value)

        return list(unique_part_nos)
            
    def get_data_with_part_no(self, part_no: str) -> List[str]:

        # file check
        if not os.path.exists(self.file_path):
            self.create_random_test_data()
            
        # You may optionally read the content you just wrote
        with open(self.file_path, "r") as f:
            csv_reader = csv.DictReader(f)

            column_types = {
                'value': float,    
                'limit_up': float,  
                'limit_down': float,  
                'part_no': str,  
                # Add more columns as needed
            }

            # Convert CSV data to a list of dictionaries with type conversions
            data_list = []
            for row in csv_reader:
                # Check if the part_no column matches the desired value
                if row.get('part_no') == part_no:
                    converted_row = {}
                    for column, value in row.items():
                        # Perform type conversion based on the defined types
                        column_type = column_types.get(column, str)
                        converted_row[column] = column_type(value)
                    data_list.append(converted_row)

        return data_list
    
    
    def save_data(self, data: Dict[Any, Any], limit: Dict[Any, Any]):
        
        with open(self.file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                
                # Write data and limits to the CSV file
                for lot_str, datetime_str, value, limit_up, limit_down, part_no in zip(data['lot_list'], data['date_list'], data['values'], limit['up'], limit['down'], data['part_no_list']):
                    writer.writerow([lot_str, datetime_str, value, limit_up, limit_down, part_no])
        return 



    def create_random_test_data(self) -> None:
        
        
        #  data1.csv
        self.delete_data_except_header()
        
        def generate_lot_from_date(date) -> str:
            date_str = date.replace('-', '').replace('_', '')
            lot = f'{date_str}01'
            return lot
        
        for index in range(10, 20):
            # year of 2022 
            start_date = datetime(2022, 1, 1)
            end_date = datetime(2022, 12, 31)
            date_range = pd.date_range(start_date, end_date, freq='D')  


            date_list = [date.strftime('%Y-%m-%d') for date in date_range]

            lot_list = [generate_lot_from_date(date) for date in date_list]

            
            num_values = len(date_list)

            num_median = 30
            values = [num_median]*num_values
            part_no_list = [f'A{index}']*num_values
            
            
            for _ in range(10):
                num_random = np.sqrt(np.random.randint(1, 100))
                values = [ (value + np.random.randint(-num_random, num_random)) for value in values]
            
            limit = {}
            limit["up"] = [60]*num_values
            limit["down"] = [0]*num_values
            
            data = {
            'lot_list': lot_list,
            'date_list': date_list,
            'values': values,
            'part_no_list': part_no_list
            }
            

            self.save_data(data, limit)
    