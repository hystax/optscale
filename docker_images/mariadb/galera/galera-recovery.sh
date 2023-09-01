#! /bin/bash

cmdline_args=$@
user=mysql
euid=$(id -u)
log_file=$(mktemp /tmp/wsrep_recovery.XXXXXX)
start_pos=''
start_pos_opt=''

log() {
	local msg="galera-recovery.sh: $@"
	# Print all messages to stderr as we reserve stdout for printing
	# --wsrep-start-position=XXXX.
	echo "$msg" >&2
}

finish() {
	rm -f "$log_file"
}

trap finish EXIT

wsrep_recover_position() {
	eval mysqld --user=$user \
			--wsrep-recover \
			--log-error="$log_file"
	if [ $? -ne 0 ]; then
		# Something went wrong, let us also print the error log so that it
		# shows up in systemctl status output as a hint to the user.
		log "Failed to start mysqld for wsrep recovery: '`cat $log_file`'"
		exit 1
	fi

	start_pos=$(sed -n 's/.*WSREP: Recovered position:\s*//p' $log_file)

	if [ -z $start_pos ]; then
		skipped="$(grep WSREP $log_file | grep 'skipping position recovery')"
		if [ -z "$skipped" ]; then
			log "=================================================="
			log "WSREP: Failed to recover position: '`cat $log_file`'"
			log "=================================================="
			exit 1
		else
			log "WSREP: Position recovery skipped."
		fi

	else
		log "Found WSREP position: $start_pos"

		# TODO Find a better solution to automatically restore after a full cluster crash
		# Force start even if some latest TX are lost before a crash
		# otherwise container just cannot start in K8s StatefulSet configuration
		sed -i 's/safe_to_bootstrap: 0/safe_to_bootstrap: 1/g' /var/lib/mysql/grastate.dat

		start_pos_opt="--wsrep_start_position=$start_pos"
	fi
}

if [ -n "$log_file" -a -f "$log_file" ]; then
	[ "$euid" = "0" ] && chown $user $log_file
	chmod 600 $log_file
else
	log "WSREP: mktemp failed"
fi

if [ -f /var/lib/mysql/ibdata1 ]; then
        if [ ! -f /var/lib/mysql/grastate.dat ]; then
		if [ "$HOSTNAME" = "mariadb0-0" ]; then
			echo "--wsrep-new-cluster"
			exit 0
		fi
	fi
	log "Attempting to recover GTID positon..."
	wsrep_recover_position
else
	log "No ibdata1 found, starting a fresh node..."
fi

echo "$start_pos_opt"

