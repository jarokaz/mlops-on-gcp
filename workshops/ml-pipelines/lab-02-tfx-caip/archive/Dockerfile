FROM gcr.io/caip-pipelines-assets/tfx:latest
WORKDIR /pipeline_source
COPY ./pipeline/*.py pipeline
COPY ./modules/*.py modules
ENV PYTHONPATH="/pipeline_source:${PYTHONPATH}"
