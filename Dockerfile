FROM apache/airflow:2.9.3

USER root

RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

#ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 для x86
#Для arm:
#ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64 
ARG TARGETARCH 
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-${TARGETARCH}
ENV PATH=$JAVA_HOME/bin:$PATH

USER airflow
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
