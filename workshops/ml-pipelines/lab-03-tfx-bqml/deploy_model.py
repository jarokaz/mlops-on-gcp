
import os
import logging
import uuid

import googleapiclient.discovery

from tfx.types.standard_artifacts import Model
from tfx.dsl.component.experimental.decorators import component
from tfx.dsl.component.experimental.annotations import InputArtifact, OutputArtifact, Parameter

@component
def deploy_model(
    project_id: Parameter[str],
    model_name: Parameter[str],
    runtime_version: Parameter[str],
    python_version: Parameter[str],
    framework: Parameter[str],
    model: InputArtifact[Model]):
    
    service = googleapiclient.discovery.build('ml', 'v1')
    version_name = f'v{uuid.uuid4().hex}'
   
    saved_model_path = '{}/serving_model_dir'.format(model.uri.rstrip('/'))
    
    project_path = f'projects/{project_id}'
    model_path = f'{project_path}/models/{model_name}'
    
    response = service.projects().models().list(parent=project_path).execute()
    if 'error' in response:
        raise RuntimeError(response['error'])
        

    if not response or not [model['name'] for model in response['models'] if model['name'] == model_path]:
        request_body={'name': model_name}
        response = service.projects().models().create(parent=project_path, body=request_body).execute()
        if 'error' in response:
            raise RuntimeError(response['error'])
        
    request_body = {
        "name": version_name,
        "deployment_uri": saved_model_path,
        "machine_type": "n1-standard-8",
        "runtime_version": runtime_version,
        "python_version": python_version,
        "framework": framework
    }
    
    logging.info(f'Starting model deployment')
    response = service.projects().models().versions().create(parent=model_path, body=request_body).execute()
    if 'error' in response:
        raise RuntimeError(response['error'])
    logging.info(f'Model deployed: {response}')
