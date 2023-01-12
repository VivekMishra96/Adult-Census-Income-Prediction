from collections import namedtuple


DataIngestionConfig = namedtuple("DataIngestionConfig",
['dataset_url','raw_dir','zip_data_dir','raw_data_file','ingested_dir',
 'ingested_train_dir','ingested_test_dir'])


DataValidationConfig = namedtuple("DataValidationConfig",
['schema_file_path','report_file_path','report_page_file_path'])


DataTransformationonfig = namedtuple("DataTransformationonfig",
['transformed_train_dir',
 'transformed_test_dir',
 'preprocessed_object_file_path'])


ModelTrainerConfig = namedtuple("ModelTrainerConfig",
['trained_model_file_path','base_accuracy','model_config_file_path'])


ModelEvaluationConfig = namedtuple("ModelEvaluationConfig",
['model_evaluation_file_path','time_stamp'])


ModelPusherConfig = namedtuple("ModelPusherConfig",
['export_dir_path'])


TrainingPipelineConfig = namedtuple("TrainingPipelineConfig",
['artifact_dir'])
