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
        '--machine_type=' + configs.DATAFLOW_MACHINE_TYPE,
        '--disk_size_gb=' + configs.DATAFLOW_DISK_SIZE,
        '--region=' + configs.GCP_REGION
    ]
    
    beam_pipeline_args = None
    
    ai_platform_training_args = {
        'project': project_id,
        'region': configs.GCP_REGION,
        'scaleTier': 'CUSTOM',
        'masterType': configs.CAIP_TRAINING_MACHINE_TYPE,
        'masterConfig': {
            'imageUri': tfx_image}      
    }
    
    ai_platform_training_args = None
    
    ai_platform_serving_args = {
        'project_id': project_id,
        'model_name': configs.MODEL_NAME,
        'runtimeVersion': configs.RUNTIME_VERSION,
        'pythonVersion': configs.PYTHON_VERSION,
        'regions': [configs.GCP_REGION]
    }

    #ai_platform_serving_args = None
    
    pipeline = pipeline.create_pipeline(
        pipeline_name=configs.PIPELINE_NAME,
        pipeline_root=pipeline_root,
        data_root=configs.DATA_ROOT,
        schema_uri=configs.SCHEMA_URI,
        preprocessing_fn=configs.PREPROCESSING_FN,
        run_fn=configs.RUN_FN,
        train_args=trainer_pb2.TrainArgs(num_steps=configs.TRAIN_NUM_STEPS),
        eval_args=trainer_pb2.EvalArgs(num_steps=configs.EVAL_NUM_STEPS),
        eval_accuracy_threshold=configs.EVAL_ACCURACY_THRESHOLD,
        serving_model_dir=configs.SERVING_MODEL_DIR,
        ai_platform_training_args=ai_platform_training_args,
        ai_platform_serving_args=ai_platform_serving_args,
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
    
    






