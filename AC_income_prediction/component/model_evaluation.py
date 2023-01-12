from operator import mod
from urllib import response
import numpy as np
from AC_income_prediction.constant import *
from AC_income_prediction.entity.config_entity import DataIngestionConfig, ModelEvaluationConfig
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, ModelEvaluationArtifact, ModelTrainerArtifact
from AC_income_prediction.logger import logging
import os,sys
from AC_income_prediction.exception import IncomePredictionException
from AC_income_prediction.util.util import load_data, load_numpy_array_data, load_object, read_yaml_file, write_yaml_file
from AC_income_prediction.entity.model_factory import evaluate_classification_model

class ModelEvaluation:
    
    def __init__(
        self,
        model_evaluation_config: ModelEvaluationConfig,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_artifact: DataValidationArtifact,
        model_trainer_artifact: ModelTrainerArtifact):
        try:
            logging.info(f"{'>>' * 30}Model Evaluation log started.{'<<' * 30} ")
            self.model_evaluation_config = model_evaluation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def get_best_model(self):
        try:
            model = None
            
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path
            
            if not os.path.exists(model_evaluation_file_path):
                write_yaml_file(file_path=model_evaluation_file_path)
                
                logging.info(f"best model: {model}")
                return model
            
            model_eval_file_content = read_yaml_file(
                file_path=model_evaluation_file_path
            )
            
            model_eval_file_content = dict() if model_eval_file_content is None else model_evaluation_file_path
            
            if BEST_MODEL_KEY not in model_eval_file_content:
                
                logging.info(f"best model: {model}")
                return model
            
            model = load_object(file_path=model_eval_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])
            
            logging.info(f"best model: {model}")
            return model
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def update_evaluation_report(
        self,
        model_evaluation_artifact : ModelEvaluationArtifact):
        try:
            eval_file_path = self.model_evaluation_config.model_evaluation_file_path
            model_eval_content = read_yaml_file(file_path=eval_file_path)
            model_eval_content = dict() if model_eval_content is None else model_eval_content
            previous_model = None
            
            if BEST_MODEL_KEY in model_eval_content:
                previous_model = model_eval_content[BEST_MODEL_KEY]
            
            logging.info(f"Previous eval result: {model_eval_content}")
            
            eval_result = {
                BEST_MODEL_KEY:{
                    MODEL_PATH_KEY: model_evaluation_artifact.evaluated_model_path
                }
            }
            
            if previous_model is not None:
                model_history = {self.model_evaluation_config.time_stamp: previous_model}
                if HISTORY_KEY not in model_eval_content:
                    history = {HISTORY_KEY:model_history}
                    eval_result.update(history)
                else:
                    model_eval_content[HISTORY_KEY].update(model_history)
                    
            model_eval_content.update(eval_result)
            logging.info(f"Updated eval result:{model_eval_content}")
            
            write_yaml_file(file_path=eval_file_path,data=model_eval_content)
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def initiate_model_evaluation(self)-> ModelEvaluationArtifact:
        try:
            trained_model_file_path = self.model_trainer_artifact.trained_model_file_path
            trained_model_object = load_object(file_path=trained_model_file_path)
            
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            schema_file_path = self.data_validation_artifact.schema_file_path
            
            train_dataframe = load_data(file_path=train_file_path,schema_file_path=schema_file_path)
            test_dataframe = load_data(file_path=test_file_path,schema_file_path=schema_file_path)
            
            schema_content = read_yaml_file(file_path=schema_file_path)
            target_column_name = schema_content[TARGET_COLUMN_KEY]
            
            # target column
            logging.info(f"Converting target column into numpy array.")
            train_target_arr = np.array(train_dataframe[target_column_name])
            test_target_arr = np.array(test_dataframe[target_column_name])
            logging.info(f"Conversion completed target column into numpy array.")
            
            # droping taget column from the dataframe
            logging.info(f"Dropping target column from the dataframe.")
            train_dataframe.drop([target_column_name],axis=1,inplace=True)
            test_dataframe.drop([target_column_name],axis=1,inplace=True)
            logging.info(f"Dropping target column from the dataframe completed.")
            
            model = self.get_best_model()
            
            if model is None:
                logging.info("Not found any existing model. Hence accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(
                    is_model_accepted=True,
                    evaluated_model_path=trained_model_file_path, 
                )
                
                self.update_evaluation_report(model_evaluation_artifact=model_evaluation_artifact)
                
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
                return model_evaluation_artifact
            
            model_list = [model,trained_model_object]
            
            metric_info_artifact = evaluate_classification_model(
                model_list=model_list,
                X_train=train_dataframe,
                y_train=train_target_arr,
                X_test=test_dataframe,
                y_test=test_target_arr,
                base_accuracy=self.model_trainer_artifact.model_accuracy
            )
            logging.info(f"Model evaluation completed. model metric artifact: {metric_info_artifact}")
            
            if metric_info_artifact is None:
                response = ModelEvaluationArtifact(
                                is_model_accepted=None,
                                evaluated_model_path=trained_model_file_path, 
                            )
                logging.info(response)
                return response
            
            if metric_info_artifact.index_number == 1:
                model_evaluation_artifact = ModelEvaluationArtifact(
                                                is_model_accepted=True,
                                                evaluated_model_path=trained_model_file_path, 
                                            )
                self.update_evaluation_report(model_evaluation_artifact=model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
            else:
                logging.info("Trained model is no better than existing model hence not accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(
                                                is_model_accepted=False,
                                                evaluated_model_path=trained_model_file_path, 
                                            )
            
            return model_evaluation_artifact
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def __del__(self):
        logging.info(f"{'=' * 20}Model Evaluation log completed.{'=' * 20} ")
             