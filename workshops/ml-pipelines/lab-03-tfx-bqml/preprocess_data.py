
import os
import logging
import uuid

from google.cloud import bigquery

from tfx.types.experimental.simple_artifacts import Dataset
from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import OutputArtifact, Parameter

@component
def preprocess_data(
    project_id: Parameter[str],
    query: Parameter[str], 
    transformed_data: OutputArtifact[Dataset]):
    
    client = bigquery.Client(project=project_id)

    dataset_name = f'{project_id}.bqml_demo_{uuid.uuid4().hex}'
    table_name = f'{dataset_name}.{uuid.uuid4().hex}'
    
    dataset = bigquery.Dataset(dataset_name)
    client.create_dataset(dataset)

    job_config = bigquery.QueryJobConfig()
    job_config.create_disposition = bigquery.job.CreateDisposition.CREATE_IF_NEEDED
    job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE
    job_config.destination = table_name

    logging.info(f'Starting data preprocessing')
    
    query_job = client.query(query, job_config)
    query_job.result() # Wait for the job to complete
    
    logging.info(f'Completed data preprocessing. Output in  {table_name}')
    
    # Write the location of the output table to metadata.  
    transformed_data.set_string_custom_property('output_dataset', dataset_name)
    transformed_data.set_string_custom_property('output_table', table_name)
