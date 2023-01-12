
from AC_income_prediction.entity.config_entity import DataIngestionConfig
from AC_income_prediction.logger import logging
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact
from AC_income_prediction.exception import IncomePredictionException
import os,sys
from six.moves import urllib
import zipfile
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np
from AC_income_prediction.constant import *


class DataIngestion:
    
    def __init__(
        self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'='*20}Data Ingestion log started.{'='*20}")
            self.data_ingestion_config = data_ingestion_config
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def download_income_prediction_data(self)-> str:
        try:
            download_url = self.data_ingestion_config.dataset_url
            
            # folder location for dataset zip file download
            # tgz_downlod_dir = self.data_ingestion_config.raw_dir
            tgz_downlod_dir = self.data_ingestion_config.zip_data_dir
            
            if os.path.exists(tgz_downlod_dir):
                os.remove(tgz_downlod_dir)
                
            os.makedirs(tgz_downlod_dir,exist_ok=True)
            
            income_prediction_file_name = os.path.basename(download_url)
            # income_prediction_file_name = "archive.zip"
            
            tgz_file_path = os.path.join(
                tgz_downlod_dir,
                income_prediction_file_name
            )
            logging.info(f"Downloading file from :[{download_url}] into :[{tgz_file_path}]")
            
            urllib.request.urlretrieve(download_url, tgz_file_path)
            logging.info(f"File :[{tgz_file_path}] has been downloaded successfully.")
            return tgz_file_path
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_dir
            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)
                
            os.makedirs(raw_data_dir,exist_ok=True)
            logging.info(f"Extracting zip file: [{tgz_file_path}] into dir: [{raw_data_dir}]")
            
            with zipfile.ZipFile(tgz_file_path, 'r') as zip_ref:
                zip_ref.extractall(path=raw_data_dir) 
            
            logging.info(f"Extraction completed")
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
        
    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_dir
            
            file_name = os.listdir(raw_data_dir)[0]
            income_prediction_file_path  = os.path.join(raw_data_dir,file_name)
            logging.info(f"Reading csv file: [{income_prediction_file_path}]")
            
            income_prediction_data_frame = pd.read_csv(income_prediction_file_path)         
            
            income_prediction_data_frame["education-num_add"] = pd.cut(
                income_prediction_data_frame["education-num"],
                bins=[0.0,3.0,6.0,9.0,12.0,15.0,18.0,np.inf],
                labels=[1,2,3,4,5,6,7]
            )
             
            logging.info(f"splitting data into train test.")
            strat_train_set = None
            strat_test_set = None
            
            split = StratifiedShuffleSplit(n_splits=10, test_size=0.2, random_state=42)
            
            for train_index, test_index in split.split(income_prediction_data_frame,income_prediction_data_frame['education-num_add']):
                strat_train_set = income_prediction_data_frame.loc[train_index].drop(['education-num_add'],axis=1)
                strat_test_set = income_prediction_data_frame.loc[test_index].drop(['education-num_add'],axis=1)
            
            train_file_path = os.path.join(
                self.data_ingestion_config.ingested_train_dir,
                file_name)
            
            test_file_path = os.path.join(
                self.data_ingestion_config.ingested_test_dir,
                file_name)
            
            if train_file_path is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)
                
            if test_file_path is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir,exist_ok=True)
                logging.info(f"Exporting testing datset to file: [{train_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)
            
            data_ingestion_artifact = DataIngestionArtifact(
                train_file_path=train_file_path,
                test_file_path=test_file_path,
                is_ingested=True,
                message="Data ingestion completed successfully."
            )
            
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            tgz_file_path = self.download_income_prediction_data()
            self.extract_tgz_file(tgz_file_path=tgz_file_path)
            
            return self.split_data_as_train_test()
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def __del__(self):
        logging.info(f"{'='*20}Data Ingestion log completed.{'='*20} \n\n")
