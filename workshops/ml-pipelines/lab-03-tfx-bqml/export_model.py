
import os
import logging
import subprocess

from google.cloud import bigquery

from tfx.types.experimental.simple_artifacts import Dataset
from tfx.types.experimental.simple_artifacts import Model as BQModel
from tfx.types.standard_artifacts import Model
from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import InputArtifact, OutputArtifact, Parameter


@component
def export_model(
    bq_model: InputArtifact[BQModel],
    model: OutputArtifact[Model]):
    
    bq_model_name = bq_model.get_string_custom_property('bq_model_name')
    gcs_path = '{}/serving_model_dir'.format(model.uri.rstrip('/'))
    
    client = bigquery.Client()
    bqml_model = bigquery.model.Model(bq_model_name)
    
    logging.info(f'Starting model extraction')
    
    extract_job = client.extract_table(bqml_model, gcs_path)
    extract_job.result() # Wait for results
    
    logging.info(f'Model extraction completed')
   
