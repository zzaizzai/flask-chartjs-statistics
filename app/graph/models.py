import csv
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, Any, List, Optional, Type, get_type_hints
from abc import ABC, abstractmethod

from flask import current_app

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from scipy.stats import truncnorm


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

        
    def get_color(self, date_start: str = None, date_end: str = None):
        part_data_control = PartDataControl()
        
        today = datetime.today()
        date_start = datetime.strptime(date_start, "%Y-%m-%d") if date_start else (today - relativedelta(months=12))
        date_end = datetime.strptime(date_end, "%Y-%m-%d") if date_end else today
        
        
        part_no_data = part_data_control.get_data_with_part_no(self.part_no, date_start = date_start, date_end = date_end)
        
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

#############
# DataModel #
#############

class BaseData(ABC):
    
    def to_dict(self):
            return {field: getattr(self, field) for field in self.get_column().keys()}
    
    @classmethod
    def get_column(cls) -> Dict[str, Type]:
        return get_type_hints(cls)


@dataclass
class PartData(BaseData):
    datetime: str = None
    lot: str = None
    limit_down: float = None
    limit_up: float = None
    part_no: str = None
    value: float = None
    parent_no: str = None
    
    @classmethod
    def get_demo_data_list(cls) -> List[str]:
        return ['AC', 'BO', 'CZ', 'WG', 'DH', 'PU']


@dataclass
class ProductData(BaseData):
    product_no: str = None
    
    @classmethod
    def get_demo_data_list(cls) -> List[str]:
        return ['PRODUCT-AC', 'PRODUCT-BO', 'PRODUCT-DZ', 'PRODUCT-WG', 'PRODUCT-DH', 'PRODUCT-PU']


@dataclass
class PartChildData(BaseData):
    product_no: str = None
    child_part_no: str = None
    
    




###############
# DataControl #
###############

class DataControlBase(ABC):
    
    COLUMN = {}
    
    def __init__(self, 
                data_name: str, 
                date_start = None, 
                date_end = None
                ):
        
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
    def save_data(self, data_list: List[object]) -> None:
        
        if len(self.COLUMN) == 0:
            return 
        
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for data in data_list:
                row_data = [getattr(data, column_name) for column_name in self.COLUMN.keys()]
                writer.writerow(row_data)

    @abstractmethod
    def get_all_unique_no(self, no_column: str) -> List[str]:
        
        if not os.path.exists(self.file_path):
            return []
        
        # You may optionally read the content you just wrote
        with open(self.file_path, "r") as f:
            csv_reader = csv.DictReader(f)
            
            # Use a set to store unique part_no values
            unique_part_nos = set()
            for row in csv_reader:
                part_no_value = row.get(no_column)
                if part_no_value not in unique_part_nos:
                    unique_part_nos.add(part_no_value)

        return list(unique_part_nos)


    @abstractmethod
    def create_random_test_data(self):
        pass


class ProductChildControl(DataControlBase):
    
    def __init__(self, data_name= 'product_child'):
        super().__init__(data_name=data_name)
        
        self.COLUMN = PartChildData().get_column()
        
    def create_random_test_data(self):
        super().create_random_test_data()

    def get_all_unique_no(self):
        pass


class ProductDataControl(DataControlBase):

    def __init__(self, 
                data_name = 'product', 
                date_start = None, 
                date_end = None
                ):
        super().__init__(
            data_name=data_name, 
            date_start=date_start, 
            date_end=date_end)
        
        self.COLUMN = ProductData().get_column()
        
        # file check
        if not os.path.exists(self.file_path):
            # create random test for demo
            self.create_random_test_data()
            
    def save_data(self, data_list: List[ProductData]) -> None:
        super().save_data(data_list)
    
    def _generate_lot_from_date(self, date) -> str:
        date_str = date.replace('-', '').replace('_', '')
        lot = f'{date_str}01'
        return lot
    
    def get_all_unique_no(self) -> List[str]:
        return super().get_all_unique_no('product_no')
        
    def get_part_no_list_of_product(self) -> List[str]:
        pass
    # TODO get part no list from product_child.csv
    
    def create_random_test_data(self) -> None:
        
        self.delete_data_except_header()
        product_no_candidate_list = ProductData().get_demo_data_list()
        
        data_obj_list = []  # Create an empty list to hold all data objects
        for _, product_name in enumerate(product_no_candidate_list):
            
            for index in range(10, 20):
                
                today = datetime.today()
                start_date = today - timedelta(days= 365)
                end_date = today
                
                date_range = pd.date_range(start_date, end_date, freq='D')  
                date_list = [date.strftime('%Y-%m-%d') for date in date_range]
                
                lot_list = [self._generate_lot_from_date(date) for date in date_list]
                
                
                num_values = len(date_list)
                
                num_median = 30
                values = [num_median]*num_values
                product_no_list = [f'{product_name}{index:03d}']*num_values
                
                
                for _ in range(10):
                    num_random = np.sqrt(np.random.randint(1, 100))
                    values = [ (value + np.random.randint(-num_random, num_random)) for value in values]
                
                limit_up_list = [60]*num_values
                limit_down_list = [0]*num_values
                
                for index, _ in enumerate(lot_list):
                    data_obj = ProductData()
                    data_obj.product_no=product_no_list[index]
                    
                    data_obj_list.append(data_obj)
                    
        self.save_data(data_obj_list)

class PartDataControl(DataControlBase):


    def __init__(self, data_name = 'data1', date_start = None, date_end = None):
        super().__init__(data_name = data_name, date_start = date_start, date_end= date_end)
        
        self.COLUMN = PartData.get_column()

        # file check
        if not os.path.exists(self.file_path):
            # create random test for demo
            self.create_random_test_data()

    
    def delete_data_except_header(self) -> None:
        super().delete_data_except_header()
        
        
    def get_all_unique_no(self) -> List[str]:
        return super().get_all_unique_no('part_no')
    
    def save_data(self, data_list: List[PartData]) -> None:
        super().save_data(data_list)

            
    def get_data_with_part_no(self, part_no: str, date_start: str, date_end: str) -> List[str]:
        
        date_start = date_start
        date_end = date_end
        
        if type(date_start) is datetime:
            date_start = date_start.strftime("%Y-%m-%d")
            
        if type(date_end) is datetime:
            date_end = date_end.strftime("%Y-%m-%d")
            
        df = pd.read_csv(self.file_path)
        # Filter data based on part_no and date range
        mask = (df['part_no'] == part_no) & (df['datetime'] >= date_start) & (df['datetime'] <= date_end)
        filtered_df = df[mask]

        # Convert the filtered DataFrame to a list of dictionaries
        data_list = filtered_df.to_dict(orient='records')
        return data_list
    
    def _generate_lot_from_date(self, date) -> str:
        date_str = date.replace('-', '').replace('_', '')
        lot = f'{date_str}01'
        return lot

    def create_random_test_data(self) -> None:
        start_time = time.time()
        self.delete_data_except_header()

        part_no_candidate_list = PartData().get_demo_data_list()
        num_part_no_child_candidate_list = [num for num in range(1, 11)]

        data_obj_list = []  # Create an empty list to hold all data objects

        for part_name in part_no_candidate_list:
            for index in range(10, 20):
                for child_index in num_part_no_child_candidate_list:
                    today = datetime.today()
                    start_date = today - timedelta(days=365)
                    end_date = today

                    date_range = pd.date_range(start_date, end_date, freq='D')
                    date_list = [date.strftime('%Y-%m-%d') for date in date_range]

                    lot_list = [self._generate_lot_from_date(date) for date in date_list]

                    num_values = len(date_list)
                    std_dev = np.random.randint(1, 20)
                    num_median = 30
                    
                    values = truncnorm.rvs((-70 - num_median) / std_dev, (70 - num_median) / std_dev, loc=num_median, scale=std_dev, size=num_values)

                    part_no_list = [f'{part_name}{index:03d}-{child_index:02d}'] * num_values
                    parent_no_list = [f'PRODUCT-{part_name}{index:03d}'] * num_values

                    limit_up_list = [60] * num_values
                    limit_down_list = [0] * num_values

                    for i, _ in enumerate(lot_list):
                        data_obj = PartData(lot=lot_list[i],
                                            limit_down=limit_down_list[i],
                                            limit_up=limit_up_list[i],
                                            part_no=part_no_list[i],
                                            value=values[i],
                                            datetime=date_list[i],
                                            parent_no=parent_no_list[i]
                                            )
                        data_obj_list.append(data_obj)  # Append the data object to the list

        # Save all data objects at once
        self.save_data(data_obj_list)

        # 코드 실행 종료 시간 기록
        end_time = time.time()

        # 실행 시간 계산 및 출력
        execution_time = end_time - start_time
        print(f"코드 실행 시간: {execution_time} 초")