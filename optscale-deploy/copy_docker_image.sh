#!/bin/bash
if [ $# -lt 2 ] ; then
    echo "Usage: <image> <user@host>"; exit 1; fi

docker save $1 | bzip2 | pv | \
     ssh $2 'bunzip2 | docker load'
