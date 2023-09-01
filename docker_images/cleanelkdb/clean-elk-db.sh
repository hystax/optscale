#!/usr/bin/env bash

#ELK_IP=elkservice.default.svc.cluster.local
#LOG_SIZE_MAX=5120
LOG_SIZE_MAX=$HX_ELK_LOG_MAX_SIZE
ELK_IP=$HX_ELK_URL
ELK_PORT=$HX_ELK_PORT
METADATA_INDEX_NAME="%25%7b%5b%40metadata%5d%5bbeat%5d%7d-"

echo "ELK address="$ELK_IP
echo "ELK log max size="$LOG_SIZE_MAX

get_size_of_logs() {
	total_log_size=$(curl -s -X GET $1":"$ELK_PORT"/_stats/store" | jq '._all.total.store.size_in_bytes')
	total_log_size=$((total_log_size / 1024 / 1024))
	return $total_log_size
}

remove_line_from_logstash() {
	cat logstash.txt | sort > logstash.tmp
	tail -n +2 logstash.tmp | sort --reverse > logstash.txt
	rm logstash.tmp
}

remove_line_from_metadata() {
	cat metadata.txt | sort > metadata.tmp
	tail -n +2 metadata.tmp | sort --reverse > metadata.txt
	rm metadata.tmp
}

remove_index_from_elk() {
	echo "DELETING "$2" INDEX FROM ELK"
	curl -s -X DELETE $1':'$ELK_PORT'/'$2
}

get_size_of_logs $ELK_IP
m_total_log_size=$?
echo "TOTAL SIZE OF LOGS="$m_total_log_size"Mb"
if [ $m_total_log_size -lt $LOG_SIZE_MAX ]; then
	echo "SIZE OF LOGS LOWER "$LOG_SIZE_MAX"Mb -> Exit 0"
	exit 0
fi

echo "SIZE OF LOGS BIGGER "$LOG_SIZE_MAX"Mb -> START TO REMOVE LOGS"
curl -s -X GET "$ELK_IP:$ELK_PORT/_cat/indices?v" > curl_test.txt
cat curl_test.txt | awk '/logstash/ { print $3 }' | sort --reverse > logstash.txt
cat curl_test.txt | awk '/metadata/ { print $3 }' | sort --reverse > metadata.txt

while [ $m_total_log_size -gt $LOG_SIZE_MAX ]; do
	m_logstash=$(tail -n -1 logstash.txt)
	m_metadata=$(tail -n -1 metadata.txt)
	logstash_date=$(echo $m_logstash | awk -F '-' '{ print $2 }')
	metadata_date=$(echo $m_metadata | awk -F '-' '{ print $2 }')

	if [ "$m_logstash" = "" ] && [ "$m_metadata" = "" ]; then
		break
	elif [ "$m_logstash" = "" ] && [ "$m_metadata" != "" ]; then
		remove_index_from_elk $ELK_IP "$METADATA_INDEX_NAME$metadata_date"
		remove_line_from_metadata
	elif [ "$m_logstash" != "" ] && [ "$m_metadata" = "" ]; then
		remove_index_from_elk $ELK_IP $m_logstash
		remove_line_from_logstash
	else
		if [ "$logstash_date" \< "$metadata_date" ]; then
			remove_index_from_elk $ELK_IP $m_logstash
			remove_line_from_logstash
		elif [ "$logstash_date" \> "$metadata_date" ]; then
			remove_index_from_elk $ELK_IP "$METADATA_INDEX_NAME$metadata_date"
			remove_line_from_metadata
		else
			remove_index_from_elk $ELK_IP $m_logstash
			remove_line_from_logstash
			remove_index_from_elk $ELK_IP "$METADATA_INDEX_NAME$metadata_date"
			remove_line_from_metadata
		fi
	fi

	get_size_of_logs $ELK_IP
	m_total_log_size=$?
	echo "NEW TOTAL SIZE OF LOGS="$m_total_log_size"Mb"
done
echo "Done"
