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

To enable uCAIP services follow the EAP onboarding process
*Instructions will be updated when the services enter Beta

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
cloudbuild.googleapis.com \
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

To provision the instance follow the [Create an new notebook instance](https://cloud.google.com/ai-platform/notebooks/docs/create-new) setup guide. Use the *TensorFlow Enterprise 2.1* no-GPU image. Leave all other settings at their default values.

After the instance is created, you can connect to [JupyterLab](https://jupyter.org/) IDE by clicking the *OPEN JUPYTERLAB* link in the [AI Platform Notebooks Console](https://console.cloud.google.com/ai-platform/notebooks/instances).

In the **JupyterLab**, open a terminal and clone this repository in the `home` folder.
```
cd
git clone https://github.com/GoogleCloudPlatform/mlops-on-gcp.git
```

From the `mlops-labs/workshops/tfx-caip-tf21` folder execute the `install.sh` script to install **TFX** and **KFP** SDKs.

```
cd mlops-on-gcp/workshops/tfx-caip-tf21
./install.sh
```

## Summary of lab exercises

### Lab-01 - TFX Components walk-through
In this lab, you will step through the configuration and execution of core TFX components using TFX interactive context. The primary goal of the lab is to get a high level understanding of a function and usage of each of the components. 

### Lab-02 - Orchestrating model training and deployment with TFX and Cloud AI Platform
In this lab you will develop, deploy and run a TFX pipeline that uses  Cloud Dataflow and Cloud AI Platform as execution runtimes.

### Lab-03 - CI/CD for a TFX pipeline
In this lab you will author a **Cloud Build** CI/CD workflow that automatically builds and deploys a TFX pipeline. You will also integrate your workflow with **GitHub**.

### Lab-04 - ML Metadata
In this lab, you will explore ML metadata and ML artifacts created by TFX pipeline runs.
