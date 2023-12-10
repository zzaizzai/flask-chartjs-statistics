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
    
class DataControl():
    
    
    def __init__(self, data_name: str):
        
        self.data_name = data_name
        self.save_dir = current_app.config["SAVE_DIR"]
        self.file_path = os.path.join(self.save_dir, f"{data_name}.csv")
        
    def delete_data_except_header(self) -> None:

        # Read the existing content of the file
        with open(self.file_path, "r", newline='') as f:
            lines = f.readlines()

        # Extract the header (first line)
        header = lines[0]

        # Write only the header back to the file
        with open(self.file_path, "w", newline='') as f:
            f.write(header)

    def read_data(self) -> List[str]:
        
        # You may optionally read the content you just wrote
        with open(self.file_path, "r") as f:
            csv_reader = csv.DictReader(f)

            column_types = {
                'value': float,    
                'limit_up': float,  
                'limit_down': float,  
                # Add more columns as needed
            }

            # Convert CSV data to a list of dictionaries with type conversions
            data_list = []
            for row in csv_reader:
                converted_row = {}
                for column, value in row.items():
                    # Perform type conversion based on the defined types
                    column_type = column_types.get(column, str)
                    converted_row[column] = column_type(value)
                data_list.append(converted_row)

        return data_list

    def save_data(self, data: Dict[Any, Any], limit: Dict[Any, Any]):
        
        with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)

                # Write headers
                headers = ["lot", "datetime", "value", "limit_up", "limit_down"]
                writer.writerow(headers)

                # Write data and limits to the CSV file
                for lot_str, datetime_str, value, limit_up, limit_down in zip(data['lot_list'], data['date_list'], data['values'], limit['up'], limit['down']):
                    writer.writerow([lot_str, datetime_str, value, limit_up, limit_down])
        return 
