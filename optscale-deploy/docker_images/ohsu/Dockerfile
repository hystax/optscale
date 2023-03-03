FROM apache/spark-py:v3.3.0
ARG SPARK_HOME=/opt/spark
USER root
COPY spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf
COPY pip.conf /etc/pip.conf
RUN mkdir $SPARK_HOME/logs
RUN chmod 777 $SPARK_HOME/logs

ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.0/hadoop-aws-3.3.0.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.11.563/aws-java-sdk-1.11.563.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-core/1.11.563/aws-java-sdk-core-1.11.563.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.563/aws-java-sdk-bundle-1.11.563.jar $SPARK_HOME/jars
ADD https://repo1.maven.org/maven2/org/apache/httpcomponents/httpcore/4.4.15/httpcore-4.4.15.jar $SPARK_HOME/jars
# TODO: check where incompatible guava version comes from
RUN rm /opt/spark/jars/guava-*
ADD https://repo1.maven.org/maven2/com/google/guava/guava/21.0/guava-21.0.jar $SPARK_HOME/jars

WORKDIR $SPARK_HOME/work-dir/ohsu
ENV PYTHONPATH $SPARK_HOME/work-dir
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./controllers ./controllers
COPY ./handlers ./handlers
COPY /*.py ./


COPY worker.py /src/worker.py

CMD ["python3", "/src/worker.py"]