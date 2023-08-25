#!/usr/bin/env bash
set -e

ROBOTS_TXT_PATH=./ui/public/robots.txt

> $ROBOTS_TXT_PATH

{
  echo "User-agent: *"
  echo "Allow: /"
} >> $ROBOTS_TXT_PATH
