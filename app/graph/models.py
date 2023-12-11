from flask import Flask, current_app
import os
from typing import Tuple, Dict, Any, List, Optional
import csv
import json


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
        
        self.data_control = DataControl('data1')
    
    def get_color(self):
        part_no_data = self.data_control.get_data_with_part_no(self.part_no)
        
        num_error = 0
        for data_part in part_no_data:
            
            if data_part['value'] > data_part['limit_up']:
                num_error += 1
            
            if data_part['value'] < data_part['limit_down']:
                num_error += 1
                
        
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
    
    
    def __init__(self, data_name: str):
        
        self.data_name = data_name
        self.save_dir = current_app.config["SAVE_DIR"]
        self.file_path = os.path.join(self.save_dir, f"{data_name}.csv")
        
    def delete_data_except_header(self) -> None:

        header = ["lot", "datetime", "value", "limit_up", "limit_down", "part_no"]

        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            
    def get_all_unique_part_no(self) -> List[str]:
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
