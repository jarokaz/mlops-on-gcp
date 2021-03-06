# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Covertype training pipeline DSL."""

import os
from typing import Optional, Dict, List, Text

import tensorflow_model_analysis as tfma
import tfx

from ml_metadata.proto import metadata_store_pb2
from tfx.extensions.google_cloud_ai_platform.pusher import executor as ai_platform_pusher_executor
from tfx.extensions.google_cloud_ai_platform.trainer import executor as ai_platform_trainer_executor
from tfx.orchestration import pipeline
from tfx.proto import trainer_pb2
from tfx.proto import example_gen_pb2
from tfx.proto import evaluator_pb2
from tfx.proto import pusher_pb2
from tfx.types import standard_artifacts


SCHEMA_FOLDER = 'schema'
EVAL_ACCURACY_UPPER_BOUND = 0.995
CHANGE_THRESHOLD = 0.0001

def create_pipeline(
    pipeline_name: Text,
    pipeline_root: Text,
    data_root: Text,
    schema_uri: Text,
    preprocessing_fn: Text,
    run_fn: Text,
    train_args: trainer_pb2.TrainArgs,
    eval_args: trainer_pb2.EvalArgs,
    eval_accuracy_threshold: float,
    serving_model_dir: Text,
    beam_pipeline_args: List[Text] = None,
    ai_platform_training_args: Dict[Text, Text] = None,
    ai_platform_serving_args: Dict[Text, Text] = None,
    enable_cache: Optional[bool] = False
) -> pipeline.Pipeline:
    """Trains and deploys the Covertype classifier."""

    components = []

    # Brings data into the pipeline and splits the data into training and eval splits
    output_config = example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(
            splits=[example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=4),
                    example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=1)]))

    example_gen = tfx.components.CsvExampleGen(
        instance_name='import_csv_data',
        input_base=data_root,
        output_config=output_config)

    components.append(example_gen)

    # Computes statistics over data for visualization and example validation.
    statistics_gen = tfx.components.StatisticsGen(
        instance_name='generate_statistics',
        examples=example_gen.outputs.examples)

    components.append(statistics_gen)

    # Import a user-provided schema
    schema_importer = tfx.components.ImporterNode(instance_name='import_user_schema',
                                 source_uri=schema_uri,
                                 artifact_type=standard_artifacts.Schema)
    
    components.append(schema_importer)

    # Generates schema based on statistics files.Even though, we use user-provided schema
    # we still want to generate the schema of the newest data for tracking and comparison
    schema_gen = tfx.components.SchemaGen(
        instance_name='auto_generate_schema',
        statistics=statistics_gen.outputs.statistics)
    
    components.append(schema_gen)
  
    # Performs anomaly detection based on statistics and data schema.
    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs.statistics, 
        schema=schema_importer.outputs.result)
    
    components.append(example_validator)
  
    # Performs transformations and feature engineering in training and serving.
    transform = tfx.components.Transform(
        examples=example_gen.outputs.examples,
        schema=schema_importer.outputs.result,
        preprocessing_fn=preprocessing_fn)
    
    components.append(transform)
    
    # Trains the model using a user provided training module
    trainer_args = {
      'run_fn': run_fn,
      'transformed_examples': transform.outputs.transformed_examples,
      'schema': schema_importer.outputs.result,
      'transform_graph': transform.outputs.transform_graph,
      'train_args': train_args,
      'eval_args': eval_args,
      'custom_executor_spec':
          tfx.components.base.executor_spec.ExecutorClassSpec(
              tfx.components.trainer.executor.GenericExecutor)
       }
    # If requested use AI Platform Training
    if ai_platform_training_args is not None:
        trainer_args.update({
            'custom_executor_spec':
                tfx.components.base.executor_spec.ExecutorClassSpec(
                    ai_platform_trainer_executor.GenericExecutor),
            'custom_config': {
                ai_platform_trainer_executor.TRAINING_ARGS_KEY: ai_platform_training_args}
    })
        
    trainer = tfx.components.Trainer(**trainer_args)
    
    components.append(trainer)
    
    # Get the latest blessed model for model validation.
    resolver = tfx.components.ResolverNode(
        instance_name='latest_blessed_model_resolver',
        resolver_class=(
            tfx.dsl.experimental.latest_blessed_model_resolver.LatestBlessedModelResolver),
        model=tfx.types.Channel(
            type=tfx.types.standard_artifacts.Model),
        model_blessing=tfx.types.Channel(
            type=tfx.types.standard_artifacts.ModelBlessing))
    
    components.append(resolver)
  
    # Uses TFMA to compute a evaluation statistics over features of a model.
    accuracy_threshold = tfma.MetricThreshold(
        value_threshold=tfma.GenericValueThreshold(
            lower_bound={'value': eval_accuracy_threshold},
            upper_bound={'value': EVAL_ACCURACY_UPPER_BOUND}),
        change_threshold=tfma.GenericChangeThreshold(
            absolute={'value': CHANGE_THRESHOLD},
            direction=tfma.MetricDirection.HIGHER_IS_BETTER))
  
    metrics_specs = tfma.MetricsSpec(
        metrics = [
            tfma.MetricConfig(class_name='SparseCategoricalAccuracy',
            threshold=accuracy_threshold),
            tfma.MetricConfig(class_name='ExampleCount')])
  
    eval_config = tfma.EvalConfig(
        model_specs=[
            tfma.ModelSpec(label_key='Cover_Type')],
        metrics_specs=[metrics_specs],
        slicing_specs=[
            tfma.SlicingSpec(),
            tfma.SlicingSpec(feature_keys=['Wilderness_Area'])])
    
    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs.examples,
        model=trainer.outputs.model,
        #baseline_model=resolver.outputs.model,
        eval_config=eval_config)

    components.append(evaluator)
  
    pusher_args = {
        'model':
            trainer.outputs.model,
        'model_blessing':
            evaluator.outputs.blessing,
        'push_destination':
            pusher_pb2.PushDestination(
                filesystem=pusher_pb2.PushDestination.Filesystem(
                    base_directory=serving_model_dir))}
    
    if ai_platform_serving_args is not None:
        pusher_args.update({
            'custom_executor_spec':
                tfx.components.base.executor_spec.ExecutorClassSpec(
                    ai_platform_pusher_executor.Executor),
            'custom_config': {
                ai_platform_pusher_executor.SERVING_ARGS_KEY: ai_platform_serving_args},
        })
        
    pusher = tfx.components.Pusher(**pusher_args)
    components.append(pusher)
    
    # Checks whether the model passed the validation steps and pushes the model
    # to a file destination or AI Platform Prediction if check passed.
  #  deploy = tfx.components.Pusher(
  #      model=train.outputs['model'],
  #      model_blessing=analyze.outputs['blessing'],
  #      infra_blessing=infra_validate.outputs['blessing'],
  #      push_destination=pusher_pb2.PushDestination(
  #          filesystem=pusher_pb2.PushDestination.Filesystem(
  #              base_directory=os.path.join(
  #                  str(pipeline.ROOT_PARAMETER), 'model_serving'))))
  #             
  # deploy = tfx.components.Pusher(
  #    custom_executor_spec=executor_spec.ExecutorClassSpec(
  #        ai_platform_pusher_executor.Executor),
  #    model=train.outputs.model,
  #    model_blessing=validate.outputs.blessing,
  #    custom_config={'ai_platform_serving_args': ai_platform_serving_args})


    return pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        #enable_cache=enable_cache,
        beam_pipeline_args=beam_pipeline_args
    )


