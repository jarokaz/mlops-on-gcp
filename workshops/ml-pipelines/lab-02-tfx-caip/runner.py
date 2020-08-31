# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Managed Pipelines runner configuration"""


import os

from absl import logging
from typing import Optional, Dict, List, Text

from tfx.orchestration.ai_platform_pipelines import ai_platform_pipelines_dag_runner
from tfx.tools.cli.ai_platform_pipelines import labels
from tfx.proto import trainer_pb2

from pipeline import configs
from pipeline import pipeline

if __name__ == '__main__':

    logging.set_verbosity(logging.INFO)

    # Currently TFX CLI passes parameters to the runner
    # using environment variables. This may change in future
    tfx_image = os.environ.get(labels.CAIPP_TFX_IMAGE_ENV)
    project_id = os.environ.get(labels.CAIPP_GCP_PROJECT_ID_ENV)
    api_key = os.environ.get(labels.CAIPP_API_KEY_ENV)

    pipeline_root = '{}/{}'.format(configs.ARTIFACT_STORE,
                                   configs.PIPELINE_NAME)
    
    beam_tmp_folder = '{}/beam/tmp'.format(configs.ARTIFACT_STORE)
    beam_pipeline_args = [
       '--runner=DataflowRunner',
       '--experiments=shuffle_mode=auto',
       '--project=' + project_id,
       '--temp_location=' + beam_tmp_folder,
       '--region=' + configs.GCP_REGION]
    
    
    pipeline = pipeline.create_pipeline(
        pipeline_name=configs.PIPELINE_NAME,
        pipeline_root=pipeline_root,
        data_root=configs.DATA_ROOT,
        beam_pipeline_args=beam_pipeline_args)
   
    runner_config = ai_platform_pipelines_dag_runner.AIPlatformPipelinesDagRunnerConfig(
        project_id=project_id,
        display_name=configs.PIPELINE_NAME,
        default_image=tfx_image
    )

    runner = ai_platform_pipelines_dag_runner.AIPlatformPipelinesDagRunner(
        config=runner_config)

    if os.environ.get(labels.CAIPP_RUN_FLAG_ENV, False):
        # Only trigger the execution when invoked by 'run' command.
        runner.run(
            pipeline=pipeline,
            api_key=api_key)
    else:
        runner.compile(
            pipeline=pipeline,
            write_out=True)
    
    
#  # Set the values for the compile time parameters
#    
#  ai_platform_training_args = {
#      'project': Config.PROJECT_ID,
#      'region': Config.GCP_REGION,
#      'masterConfig': {
#          'imageUri': Config.TFX_IMAGE,
#      }
#  }
#
#  ai_platform_serving_args = {
#      'project_id': Config.PROJECT_ID,
#      'model_name': Config.MODEL_NAME,
#      'runtimeVersion': Config.RUNTIME_VERSION,
#      'pythonVersion': Config.PYTHON_VERSION,
#      'regions': [Config.GCP_REGION]
#  }
#

#  
#  # Set the default values for the pipeline runtime parameters
#    
#  data_root_uri = data_types.RuntimeParameter(
#      name='data-root-uri',
#      default=Config.DATA_ROOT_URI,
#      ptype=Text
#  )
#
#  train_steps = data_types.RuntimeParameter(
#      name='train-steps',
#      default=5000,
#      ptype=int
#  )
#    
#  eval_steps = data_types.RuntimeParameter(
#      name='eval-steps',
#      default=500,
#      ptype=int
#  )
#
#  pipeline_root = '{}/{}/{}'.format(
#      Config.ARTIFACT_STORE_URI, 
#      Config.PIPELINE_NAME,
#      kfp.dsl.RUN_ID_PLACEHOLDER)
#    
#  # Set KubeflowDagRunner settings
#  metadata_config = kubeflow_dag_runner.get_default_kubeflow_metadata_config()
#
#  runner_config = kubeflow_dag_runner.KubeflowDagRunnerConfig(
#      kubeflow_metadata_config = metadata_config,
#      pipeline_operator_funcs = kubeflow_dag_runner.get_default_pipeline_operator_funcs(
#          Config.USE_KFP_SA == 'True'),
#      tfx_image=Config.TFX_IMAGE)
#
#  # Compile the pipeline
#  kubeflow_dag_runner.KubeflowDagRunner(config=runner_config).run(
#      create_pipeline(
#        pipeline_name=Config.PIPELINE_NAME,
#        pipeline_root=pipeline_root,
#        data_root_uri=data_root_uri,
#        train_steps=train_steps,
#        eval_steps=eval_steps,
#        ai_platform_training_args=ai_platform_training_args,
#        ai_platform_serving_args=ai_platform_serving_args,
#        beam_pipeline_args=beam_pipeline_args))
#     
#        
#



