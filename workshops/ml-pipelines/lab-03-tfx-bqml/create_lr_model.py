
import os
import logging

from google.cloud import bigquery

from tfx.types.experimental.simple_artifacts import Dataset
from tfx.types.experimental.simple_artifacts import Model as BQModel
from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import InputArtifact, OutputArtifact, Parameter

@component
def create_lr_model(
    project_id: Parameter[str],
    model_name: Parameter[str],
    label_column: Parameter[str],
    transformed_data: InputArtifact[Dataset],
    model: OutputArtifact[BQModel]):
    
    dataset_name = transformed_data.get_string_custom_property('output_dataset')
    table_name = transformed_data.get_string_custom_property('output_table')
    model_name = f'{dataset_name}.{model_name}'
    
    query = f"""
        CREATE OR REPLACE MODEL
        `{model_name}`
        OPTIONS
          ( model_type='LOGISTIC_REG',
            auto_class_weights=TRUE,
            input_label_cols=['{label_column}']
          ) AS
        SELECT 
          *
        FROM
          `{table_name}`
    """
    
    client = bigquery.Client(project=project_id)

    logging.info(f'Starting training of the model: {model_name}')
    query_job = client.query(query)
    query_job.result()
    logging.info(f'Completed training of the model: {model_name}')
    
    # Write the location of the output table to metadata.  
    model.set_string_custom_property('bq_model_name', model_name)
    
