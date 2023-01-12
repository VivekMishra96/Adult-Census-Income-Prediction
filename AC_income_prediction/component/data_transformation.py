

import os,sys
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact
from AC_income_prediction.entity.config_entity import DataTransformationonfig
from AC_income_prediction.logger import logging
from AC_income_prediction.exception import IncomePredictionException
from sklearn import preprocessing
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from AC_income_prediction.constant import *
import numpy as np
import pandas as pd


from AC_income_prediction.util.util import load_data, read_yaml_file, save_numpy_array_data, save_object


class DataTransformaion:
    
    def __init__(self,
                 data_transformation_config: DataTransformationonfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact
                 ):
        try:
            logging.info(f"{'=' * 20}Data Transformation log started.{'=' * 20} ")
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def get_data_transformer_object(self)->ColumnTransformer:
        try:
            schema_file_path = self.data_validation_artifact.schema_file_path
            dataset_schema = read_yaml_file(file_path=schema_file_path)
            
            numerical_columns = dataset_schema[NUMERICAL_COLUMN_KEY]
            categorical_columns = dataset_schema[CATEGORICAL_COLUMN_KEY]
            
            num_pipeline = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy="median")),
                ('scaler', StandardScaler())
            ])
            
            cat_pipeline = Pipeline(steps=[
                ('imputer',SimpleImputer(strategy='most_frequent')),
                ('one_hot_encoder', OneHotEncoder()),
                ('scaler', StandardScaler(with_mean=False))
            ])
            
            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")
            
            preprocessing = ColumnTransformer([
                ('num_pipeline', num_pipeline, numerical_columns),
                ('cat_pipeline', cat_pipeline, categorical_columns)
            ])
            return preprocessing
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def initiate_data_transformation(self)->DataTransformationArtifact:
        try:
            logging.info(f"Obtaining preprocessing object.")
            preprocessing_obj = self.get_data_transformer_object()
            
            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            schema_file_path = self.data_validation_artifact.schema_file_path
            
            logging.info(f"Loading training and test data as pandas dataframe.")
            train_df = load_data(file_path=train_file_path,schema_file_path=schema_file_path)
            
            test_df = load_data(file_path=test_file_path,schema_file_path=schema_file_path)
            
            schema = read_yaml_file(file_path=schema_file_path)
            
            target_column_name = schema[TARGET_COLUMN_KEY]
            
            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df = train_df[target_column_name].map({' <=50K':0,' >50K':1})
            
            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name].map({' <=50K':0,' >50K':1})
            
            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
            
            train_arr = np.c_[input_feature_train_arr.toarray(),np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr.toarray(),np.array(target_feature_test_df)]
            
            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir
            
            train_file_name = os.path.basename(train_file_path).replace(".csv",".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv",".npz")
            
            transformed_train_file_path = os.path.join(
                transformed_train_dir,
                train_file_name
            )
            
            transformed_test_file_path = os.path.join(
                transformed_test_dir,
                test_file_name
            )
            
            logging.info(f"Saving transformed training and testing array.")
            
            save_numpy_array_data(file_path=transformed_train_file_path,array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path,array=test_arr)
            
            preprocessed_object_file_path = self.data_transformation_config.preprocessed_object_file_path
            
            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessed_object_file_path,obj=preprocessing_obj)
            
            
            data_transformation_artifact = DataTransformationArtifact(
                is_transformed=True,
                message="Data Transformation successfull.",
                transformed_train_file_path=transformed_train_file_path,
                transformed_test_file_path=transformed_test_file_path,
                preprocessed_object_file_path=preprocessed_object_file_path
            )
            logging.info(f"Data transformationa artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def __del__(self):
        logging.info(f"{'='*20}Data Transformation log completed.{'='*20} \n\n")
