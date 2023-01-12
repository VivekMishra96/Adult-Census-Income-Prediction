import os,sys
import pandas as pd
from AC_income_prediction.exception import IncomePredictionException
from AC_income_prediction.util.util import load_object


class IncomePredictionData:
    def __init__(
        self, age:int, workclass: str, fnlwgt: int,
        education_num:int, material_status: str,
        occupation: str, relationship: str,
        race: str, sex: str, capital_gain: int, 
        capital_loss: int, hours_per_week: int, 
        native_country: str,wages: str):
        try:
            self.age = age
            self.workclass = workclass
            self.fnlwgt = fnlwgt
            self.education_num = education_num
            self.material_status = material_status
            self.occupation = occupation
            self.relationship = relationship
            self.race = race
            self.sex = sex
            self.capital_gain = capital_gain
            self.capital_loss = capital_loss
            self.hours_per_week = hours_per_week
            self.native_country = native_country
            self.wages = wages
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def get_input_prediction_input_dataframe(self):
        try:
            income_input_data = self.get_income_prediction_data_as_dict()
            return pd.DataFrame(income_input_data)
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
    
    def get_income_prediction_data_as_dict(self):
        try:
            input_data = { 
                            "age" : [self.age],
                            "workclass" : [self.workclass],
                            "fnlwgt" : [self.fnlwgt],
                            "education_num" : [self.education_num], 
                            "material_status" : [self.material_status], 
                            "occupation" : [self.occupation],
                            "relationship" : [self.relationship],
                            "race" : [self.race],
                            "sex" : [self.sex],
                            "capital_gain" : [self.capital_gain], 
                            "capital_loss" : [self.capital_loss],
                            "hours_per_week" : [self.hours_per_week], 
                            "native_country" : [self.native_country],
                            "wages" : [self.wages] 
                        }
            return input_data
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    
        
class IncomePredictionPredictor:
    def __init__(self,model_dir:str):
        try:
            self.model_dir = model_dir
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def get_latest_model_path(self)-> str:
        try:
            folder_name = list(map(int,os.listdir(self.model_dir)))
            latest_model_dir = os.path.join(
                self.model_dir,f"{max(folder_name)}"
            )
            file_name = os.listdir(latest_model_dir[0])
            latest_model_path = os.path.join(
                latest_model_dir,
                file_name
            )
            
            return latest_model_path
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def predict(self,X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            income_value = model.predict(X)
            
            return income_value
        except Exception as e:
            raise IncomePredictionException(e,sys) from e