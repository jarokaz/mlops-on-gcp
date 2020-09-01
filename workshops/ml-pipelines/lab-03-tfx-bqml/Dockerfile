FROM gcr.io/caip-pipelines-assets/tfx:latest
RUN pip install --upgrade google-cloud-core==1.3.0 google-cloud-bigquery==1.26.1
WORKDIR /pipeline
COPY *.py ./
ENV PYTHONPATH="/pipeline:${PYTHONPATH}"
