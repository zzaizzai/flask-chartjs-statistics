import csv
import json
import os
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, List, Optional
from abc import ABC, abstractmethod

from flask import Flask, current_app

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


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
    
    def __init__(self, part_no: str):
        self.part_no = part_no

        
    def get_color(self, date_start = None, date_end = None):
        part_data_control = PartDataControl()
        part_no_data = part_data_control.get_data_with_part_no(self.part_no)
        
        today = datetime.today()
        date_start = datetime.strptime(date_start, "%Y-%m-%d") if date_start  else (today - relativedelta(months=12)).strftime("%Y-%m-%d")
        date_end = datetime.strptime(date_end, "%Y-%m-%d") if date_end else today.strftime("%Y-%m-%d")
        
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
    
    def __init__(self, datetime = None, lot: str = None, limit_down: float = None, limit_up: float = None, part_no: str = None, value: float = None):
        self.datetime = datetime
        self.lot = lot
        self.limit_down = limit_down
        self.limit_up = limit_up
        self.part_no = part_no
        self.value = value
        
    def to_dict(self):
        return {
            'datetime': self.datetime,
            'lot': self.lot,
            'limit_down': self.limit_down,
            'limit_up': self.limit_up,
            'part_no': self.part_no,
            'value': self.value
        }

    @classmethod
    def get_column(cls) -> Dict[str, Any]:
        column = {
                'lot': str,    
                'value': float,    
                'datetime': str, 
                'limit_up': float,  
                'limit_down': float,  
                'part_no': str,  
                # Add more columns as needed
                }
        return column
        

class DataControl(ABC):
    
    COLUMN = {}
    
    def __init__(self, data_name: str, date_start = None, date_end = None):
        
        self.data_name = data_name
        self.save_dir = current_app.config["SAVE_DIR"]
        self.file_path = os.path.join(self.save_dir, f"{data_name}.csv")
        self.date_start = date_start 
        self.date_end = date_end 
        
    def delete_data_except_header(self) -> None:

        header = list(self.COLUMN.keys())

        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)


    @abstractmethod
    def save_data(self):
        pass


    @abstractmethod
    def create_random_test_data(self):
        pass

class PartDataControl(DataControl):


    def __init__(self, data_name = 'data1', date_start = None, date_end = None):
        super().__init__(data_name=data_name, date_start=date_start, date_end=date_end)
        self.COLUMN = PartData().get_column()
    
    def delete_data_except_header(self) -> None:
        super().delete_data_except_header()
        
        
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
    
    def save_data(self, data_list: List[PartData]) -> None:
        
        if len(self.COLUMN) == 0:
            return 
        
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for data in data_list:
                # 데이터 형식에 맞게 데이터를 추출하여 저장
                row_data = [getattr(data, column_name) for column_name in self.COLUMN.keys()]
                writer.writerow(row_data)

            
    def get_data_with_part_no(self, part_no: str) -> List[str]:

        # file check
        if not os.path.exists(self.file_path):
            self.create_random_test_data()
            
        # You may optionally read the content you just wrote
        with open(self.file_path, "r") as f:
            csv_reader = csv.DictReader(f)
            
            # Convert CSV data to a list of dictionaries with type conversions
            data_list = []
            for row in csv_reader:
                # Check if the part_no column matches the desired value
                if row.get('part_no') == part_no:
                    # Check if a date filter is provided
                    if self.date_start and self.date_end:
                        row_date = row.get('datetime')  # Assuming 'date' is the name of the date column
                        if self.date_start <= row_date <= self.date_end:
                            converted_row = {}
                            for column, value in row.items():
                                # Perform type conversion based on the defined types
                                column_type = self.COLUMN.get(column, str)
                                converted_row[column] = column_type(value)
                            data_list.append(converted_row)
                    else:
                        converted_row = {}
                        for column, value in row.items():
                            # Perform type conversion based on the defined types
                            column_type = self.COLUMN.get(column, str)
                            converted_row[column] = column_type(value)
                        data_list.append(converted_row)

        return data_list
    
    def _generate_lot_from_date(self, date) -> str:
        date_str = date.replace('-', '').replace('_', '')
        lot = f'{date_str}01'
        return lot

    def create_random_test_data(self) -> None:
        
        self.delete_data_except_header()
        
        for index in range(10, 20):
            # year of 2022 
            today = datetime.today()
            start_date = today - timedelta(days= 365)
            end_date = today
            date_range = pd.date_range(start_date, end_date, freq='D')  
            
            date_list = [date.strftime('%Y-%m-%d') for date in date_range]
            
            lot_list = [self._generate_lot_from_date(date) for date in date_list]
            
            
            num_values = len(date_list)
            
            num_median = 30
            values = [num_median]*num_values
            part_no_list = [f'A{index}']*num_values
            
            
            for _ in range(10):
                num_random = np.sqrt(np.random.randint(1, 100))
                values = [ (value + np.random.randint(-num_random, num_random)) for value in values]
            
            limit_up_list = [60]*num_values
            limit_down_list = [0]*num_values
            
            data_obj_list= []
            for index, _ in enumerate(lot_list):
                data_obj = PartData(lot = lot_list[index], 
                                    limit_down=limit_down_list[index], 
                                    limit_up=limit_up_list[index],
                                    part_no=part_no_list[index],
                                    value = values[index],
                                    datetime=date_list[index]
                                    )
                data_obj_list.append(data_obj)
                
            self.save_data(data_obj_list)