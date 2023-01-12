from threading import Thread
from AC_income_prediction.component.data_ingestion import DataIngestion
from AC_income_prediction.component.data_transformation import DataTransformaion
from AC_income_prediction.component.data_validation import DataValidation

from AC_income_prediction.config.configuration import Configuration
from AC_income_prediction.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact, DataValidationArtifact
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
        
    def start_model_trainer(self)-> DataIngestionArtifact:
        try:
            pass
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def start_model_evaluation(self)-> DataIngestionArtifact:
        try:
            pass
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
    
    def start_model_pusher(self)-> DataIngestionArtifact:
        try:
            pass
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
            
        except Exception as e:
            raise IncomePredictionException(e,sys) from e 
