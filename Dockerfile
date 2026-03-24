FROM apache/airflow:2.9.3

USER root

RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

#ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 для x86
#Для arm:
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64 


ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow

RUN mkdir -p /tmp/spark && chmod -R 777 /tmp/spark
RUN pip install --no-cache-dir --default-timeout=1000 pyspark==3.5.1
RUN pip install --no-cache-dir apache-airflow-providers-postgres==5.10.0