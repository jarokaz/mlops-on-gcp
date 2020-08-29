FROM gcr.io/caip-pipelines-assets/tfx:latest
WORKDIR /pipeline
COPY ./*.py ./
ENV PYTHONPATH="/pipeline:${PYTHONPATH}"
