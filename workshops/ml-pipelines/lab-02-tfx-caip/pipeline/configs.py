# Copyright 2020 Google LLC. All Rights Reserved.
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
"""The pipeline configurations.
"""

import os


PIPELINE_NAME=os.getenv("PIPELINE_NAME", "tfx_covertype_continuous_training")
ARTIFACT_STORE=os.getenv("ARTIFACT_STORE", "gs://mlops-dev-env-artifact-store")
DATA_ROOT=os.getenv("DATA_ROOT", "gs://workshop-datasets/covertype/small")
#MODEL_NAME=os.getenv("MODEL_NAME", "covertype_classifier")
#GCP_REGION=os.getenv("GCP_REGION", "us-central1")
#RUNTIME_VERSION=os.getenv("RUNTIME_VERSION", "2.1")
#PYTHON_VERSION=os.getenv("PYTHON_VERSION", "3.7")
 
