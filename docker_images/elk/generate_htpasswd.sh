#!/usr/bin/env bash
set -e
htpasswd -b -n ${HTPASSWD_USER} ${HTPASSWD_PASS} > /etc/nginx/.htpasswd
