
import json
import pandas as pd
from AC_income_prediction.entity.config_entity import DataValidationConfig
from AC_income_prediction.logger import logging
import os,sys
import re
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from AC_income_prediction.exception import IncomePredictionException
from AC_income_prediction.util.util import read_yaml_file
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab


class DataValidation:
    
    def __init__(self,data_validation_config: DataValidationConfig,data_ingestion_artfact: DataIngestionArtifact):
        try:
            logging.info(f"{'='*20}Data Valdaition log started.{'='*20} \n\n")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artfact = data_ingestion_artfact
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
    
    def get_train_and_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artfact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artfact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
    
    def is_train_test_file_exists(self)->bool:
        try:
            logging.info("Checking if training and test file is available")
            is_train_file_exist = False
            is_test_file_exist = False
            
            train_file_path = self.data_ingestion_artfact.train_file_path
            test_file_path = self.data_ingestion_artfact.test_file_path
            
            is_train_file_exist = os.path.exists(train_file_path)
            is_test_file_exist = os.path.exists(test_file_path)
            
            is_available = is_train_file_exist and is_test_file_exist
            
            logging.info(f"Is train and test file exists?-> {is_available}")
            
            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                message=f"Training file: {training_file} or Testing file: {testing_file} is not present"
                raise Exception(message)
            
            return is_available
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def validate_dataset_schema(self)->bool:
        try:
            validation_status = False
            
            # read schema information
            schema_info = read_yaml_file(self.data_validation_config.schema_file_path)
            schema_columns = list(schema_info["columns"].keys())
            # schema_domain_values = list(schema_columns["domain_value"]["marital-status","sex"])
            
            tmp_list = list()
            tmp_list.extend(schema_info["domain_value"]["marital-status"])
            tmp_list.extend(schema_info["domain_value"]["sex"])
            schema_domain_values = tmp_list

            schema_number_of_columns = len(schema_columns)
            
            # read train test file
            df_train,df_test = self.get_train_and_test_df()
            
            # Read train file information
            train_columns = list(df_train.columns)
            train_no_of_columns = len(train_columns)
            # train_domain_values = list(df_train["marital-status","sex"].value_counts().index)
            
            tmp_list = list()
            tmp_list.extend(list(df_train["marital-status"].value_counts().index))
            tmp_list.extend(list(df_test["sex"].value_counts().index))
            train_domain_values = tmp_list
            
            # read test file information
            test_columns = list(df_test.columns)
            test_no_of_columns = len(test_columns)
            # test_domain_values = list(df_test["marital-status","sex"].value_counts().index)
            
            tmp_list = list()
            tmp_list.extend(list(df_test["marital-status"].value_counts().index))
            tmp_list.extend(list(df_test["sex"].value_counts().index))
            test_domain_values = tmp_list
        
            
            #1. Check column names
            is_number_of_columns_match = (schema_number_of_columns == train_no_of_columns) and (schema_number_of_columns == test_no_of_columns)
            schema_columns.sort()
            train_columns.sort()
            test_columns.sort()
            
            if (schema_columns == train_columns) and (schema_columns == test_columns):
                is_name_of_columns_match = True
            else:
                is_name_of_columns_match = False
                
            
            #2. Check the value of ocean proximity
            schema_domain_values.sort()
            train_domain_values.sort()
            test_domain_values.sort()
            
            is_domain_value_match = None
            if (schema_domain_values == train_domain_values) and (schema_domain_values == test_domain_values):
                is_domain_value_match = True
            else:
                is_domain_value_match == False
                
            if not is_domain_value_match:
                pass    
            
            validation_status = is_number_of_columns_match and is_domain_value_match and is_name_of_columns_match
            
            return validation_status
            # return True
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def get_and_save_data_drift_report(self):
        try:
            
            profile = Profile(sections=[DataDriftProfileSection()])
            
            train_df,test_df = self.get_train_and_test_df()
            
            profile.calculate(train_df,test_df)
            
            report = json.loads(profile.json())
            
            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir,exist_ok=True)
            
            with open(report_file_path,"w") as report_file:
                json.dump(report,report_file,indent=6)
            
            return report
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def save_data_drift_report_page(self):
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()])
            train_df,test_df = self.get_train_and_test_df()
            dashboard.calculate(train_df,test_df)
            
            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)
            os.makedirs(report_page_dir,exist_ok=True)
            
            dashboard.save(report_page_file_path)
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def is_data_drift_found(self)->bool:
        try:
            report = self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
        
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            self.is_train_test_file_exists()
            self.validate_dataset_schema()
            self.is_data_drift_found()
            
            schema_file_path=self.data_validation_config.schema_file_path,
            report_page_file_path=self.data_validation_config.report_page_file_path,
            report_file_path= self.data_validation_config.report_file_path,
            
            
            data_validation_artifact = DataValidationArtifact(
                schema_file_path=schema_file_path[0],
                report_page_file_path=report_page_file_path[0],
                report_file_path=report_file_path[0],
                is_validated=True,
                message="Data Validation Perform successully."
            )
            
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise IncomePredictionException(e,sys) from e
    
