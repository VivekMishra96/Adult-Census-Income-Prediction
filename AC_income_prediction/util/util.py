import sys
import yaml

from AC_income_prediction.exception import IncomePredictionException
import os,sys
import pandas as pd
from AC_income_prediction.constant import *
import numpy as np
import dill


def read_yaml_file(file_path:str)->dict:
    """
    Reads a YAML file and returns the contents as a dictionary.
    file_path: str
    """
    try:
        with open(file_path,'rb') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise IncomePredictionException(e,sys) from e 


def write_yaml_file(file_path:str, data:dict=None):
    """
    Create yaml file 
    file_path: str
    data: dict
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        
        with open(file_path,"w") as yaml_file:
            if data is not None:
                yaml.dump(data,yaml_file)
    except Exception as e:
        raise IncomePredictionException(e,sys) from e


def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok=True)
        
        with open(file_path,'wb') as file_obj:
            np.save(file_obj,array)
            
    except Exception as e:
        raise IncomePredictionException(e,sys) from e


def load_numpy_array_data(file_path:str)->np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path,"rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise IncomePredictionException(e,sys) from e 


def save_object(file_path:str, obj):
    """
    file_path: str
    obj: Any sort of object
    """
    try:
        dir_path = os.path.dirname(file_path)
        
        os.makedirs(dir_path,exist_ok=True)
        
        with open(file_path,"wb") as file_obj:
            dill.dump(obj,file_obj)
            
    except Exception as e:
        raise IncomePredictionException(e,sys) from e 


def load_object(file_path:str):
    """
    file_path:str
    """
    try:
        with open(file_path,'rb') as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise IncomePredictionException(e,sys) from e
    
    
def load_data(file_path:str,schema_file_path:str)-> pd.DataFrame:
    try:
        dataset_schema = read_yaml_file(file_path=schema_file_path)
        schema = dataset_schema[DATASET_SCHEMA_COLUMNS_KEY]
        dataframe = pd.read_csv(file_path,index_col=False)
        dataframe.rename(columns = {"education-num":"education_num",
                                    "marital-status":"marital_status",
                                    "capital-gain":"capital_gain",
                                    "capital-loss":"capital_loss",
                                    "hours-per-week":"hours_per_week"}, inplace = True)

        error_message = ""
        
        for column in dataframe.columns:
            if column in list(schema):
                dataframe[column].astype(schema[column])
            else:
                error_message = f"{error_message} \nColumn: [{column}] is not in the schema."
        
        if len(error_message) > 0:
            raise Exception(error_message)
        
        return dataframe
    
    except Exception as e:
        raise IncomePredictionException(e,sys) from e 
