This is a listener service for spark agent logs. Set parameter for spark-submit
command to redirect logs from spark agent to pharos_receiver:
--conf spark.delight.collector.url=https://<cluster_ip>/pharos_receiver/v2/collector
