







from threading import Thread
from AC_income_prediction.component.data_ingestion import DataIngestion
from AC_income_prediction.component.data_transformation import DataTransformaion
from AC_income_prediction.component.data_validation import DataValidation
from AC_income_prediction.component.model_evaluation import ModelEvaluation
from AC_income_prediction.component.model_pusher import ModelPusher
from AC_income_prediction.component.model_trainer import ModelTrainer

from AC_income_prediction.config.configuration import Configuration
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact, ModelEvaluationArtifact, ModelPusherArtifact, ModelTrainerArtifact
from AC_income_prediction.exception import IncomePredictionException
import sys,os

class Pipeline(Thread):
    
    def __init__(self,config: Configuration = Configuration()) -> None:
        try:
            self.config = config

        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def start_data_ingestion(self)-> DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config.get_data_ingestion_config())
            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact)-> DataValidationArtifact:
        try:
            data_validation = DataValidation(
                data_validation_config=self.config.get_data_validation_config(),
                data_ingestion_artfact=data_ingestion_artifact
            )
            return data_validation.initiate_data_validation()
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def start_data_transformation(self,data_ingestion_artifact:DataIngestionArtifact,
                                  data_validation_artifact:DataValidationArtifact,
                                  )-> DataTransformationArtifact:
        try:
            data_transformation = DataTransformaion(
                data_transformation_config=self.config.get_data_transformation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            return data_transformation.initiate_data_transformation()
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
    def start_model_trainer(
        self,
        data_transformation_artifact:DataTransformationArtifact
        )-> ModelTrainerArtifact:
        try:
            model_trainer = ModelTrainer(
                model_trainer_config=self.config.get_model_trainer_config(),
                data_transformation_artifact=data_transformation_artifact
            )
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def start_model_evaluation(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_artifact: DataValidationArtifact,
        Model_trainer_artifact: ModelTrainerArtifact
        )-> ModelEvaluationArtifact:
        try:
            model_eval = ModelEvaluation(
                data_ingestion_artifact = data_ingestion_artifact,
                data_validation_artifact = data_validation_artifact,
                model_trainer_artifact = Model_trainer_artifact,
                model_evaluation_config = self.config.get_model_evaluation_config()
            )
            
            return model_eval.initiate_model_evaluation()
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def start_model_pusher(
        self,
        model_eval_artifact: ModelEvaluationArtifact)-> ModelPusherArtifact:
        try:
            model_pusher = ModelPusher(
                model_pusher_config=self.config.get_model_pusher_config(),
                model_evaluation_artifact=model_eval_artifact
            )
            
            return model_pusher.initiate_model_pusher()
        
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(
                data_ingestion_artifact=data_ingestion_artifact,
            )
            data_transformation_artifact = self.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            model_trainer_artifact = self.start_model_trainer(
                data_transformation_artifact=data_transformation_artifact
            )
            model_evaluation_artifact = self.start_model_evaluation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact,
                Model_trainer_artifact=model_trainer_artifact
            )
            model_pusher_artifact = self.start_model_pusher(
                model_eval_artifact=model_evaluation_artifact
            )
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
        
        
