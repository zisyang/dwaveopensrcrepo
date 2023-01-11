FROM apache/airflow:2.4.2
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         zip unzip \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --no-cache-dir scikit-learn
RUN pip install --no-cache-dir dwave-system
RUN pip install --no-cache-dir dwave-ocean-sdk
RUN pip install --no-cache-dir dimod
