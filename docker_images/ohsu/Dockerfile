FROM apache/spark-py:v3.3.0
ARG SPARK_HOME=/opt/spark
USER root
COPY docker_images/ohsu/spark-defaults.conf $SPARK_HOME/conf/spark-defaults.conf
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

WORKDIR $SPARK_HOME/work-dir/
ENV PYTHONPATH $SPARK_HOME/work-dir/

COPY tools/optscale_exceptions tools/optscale_exceptions
COPY optscale_client/config_client optscale_client/config_client
COPY optscale_client/rest_api_client optscale_client/rest_api_client

COPY docker_images/ohsu/requirements.txt docker_images/ohsu/
RUN pip install --no-cache-dir -r docker_images/ohsu/requirements.txt
COPY docker_images/ohsu/controllers docker_images/ohsu/controllers
COPY docker_images/ohsu/handlers docker_images/ohsu/handlers
COPY docker_images/ohsu/*.py docker_images/ohsu/

CMD ["python3", "docker_images/ohsu/worker.py"]