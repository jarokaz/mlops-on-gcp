# Introduction to Managed Pipelines

This series of hands on labs introduces core concepts and development techniques for Managed Pipelines.


## Preparing the lab environment
You will use the lab environment configured as on the below diagram:

![Lab env](/images/managed-lab.png)

The core services in the environment are:
- Unified AI Platform 
    - ML experimentation and development - AI Platform Notebooks 
    - Serverless model training - AI Platform Training  
    - Serverless model serving and monitoring - AI Platform Prediction 
    - Orchestration and ML Metadata  - AI Platform Managed Pipelines
- Auxiliary services:
    - Distributed data processing - Cloud Dataflow  
    - Analytics data warehouse - BigQuery 
    - ML artifact and data stores - Google Cloud Storage 
    - Container images - Container Registry

    
In the lab environment, all services are provisioned in the same [Google Cloud Project](https://cloud.google.com/storage/docs/projects). 

### Enabling Cloud Services

To enable and configure uCAIP services follow the EAP onboarding process

*Instructions will be updated when the services enter Beta*

To enable auxiliary services:
1. Launch [Cloud Shell](https://cloud.google.com/shell/docs/launching-cloud-shell)
2. Set your project ID
```
PROJECT_ID=[YOUR PROJECT ID]

gcloud config set project $PROJECT_ID
```
3. Use `gcloud` to enable the services
```
gcloud services enable \
container.googleapis.com \
cloudresourcemanager.googleapis.com \
iam.googleapis.com \
containerregistry.googleapis.com \
containeranalysis.googleapis.com \
ml.googleapis.com \
dataflow.googleapis.com 
```

### Creating an instance of AI Platform Notebooks

An instance of **AI Platform Notebooks** is used as a primary experimentation/development workbench.

To provision the instance follow the [Create an new notebook instance](https://cloud.google.com/ai-platform/notebooks/docs/create-new) setup guide. Use the *Python 2 and 3 image* no-GPU image. Leave all other settings at their default values.

After the instance is created, you can connect to [JupyterLab](https://jupyter.org/) IDE by clicking the *OPEN JUPYTERLAB* link in the [AI Platform Notebooks Console](https://console.cloud.google.com/ai-platform/notebooks/instances).

### Installing TFX SDK

1. In the **JupyterLab**, open a new terminal
2. Install Skaffold
```
curl -Lo skaffold  https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && chmod +x skaffold && mkdir -p /home/jupyter/.local/bin && mv skaffold /home/jupyter/.local/bin/
```
3. Install TFX SDK
```
pip install pip --upgrade
export SDK_VERSION='tfx-0.22.0.caip.latest-py3-none-any.whl'
export SDK_VERSION='tfx-0.23.0.caip.latest-py3-none-any.whl'
export SDK_LOCATION=gs://caip-pipelines-sdk/releases/latest/${SDK_VERSION}
gsutil cp ${SDK_LOCATION} /tmp/${SDK_VERSION} 
pip install --user --no-cache-dir /tmp/${SDK_VERSION}
```


## Summary of lab exercises

### Lab-01 - TFX Components walk-through
In this lab, you will step through the configuration and execution of core TFX components using TFX interactive context. The primary goal of the lab is to get a high level understanding of a function and usage of each of the components. 

### Lab-02 - Implementing continuous training pipeline for TensorFlow
In this lab you will develop, deploy and run a pipeline that uses TFX components to train and deploy a TensorFlow model.

### Lab-03 - Implementing continuous training pipeline for BQML
In this lab you will develop, deploy and run a pipeline that uses custom components to train and deploy a BQML model.


