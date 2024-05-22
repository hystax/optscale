#!/usr/bin/env bash
#-------------------------------------------------------------------
# Hystax
# Copyright 2016-2024 Hystax
# All Rights Reserved
#
# NOTICE:  Hystax permits you to use this file in accordance
# with the terms of the Hystax license agreement
# accompanying it.  If you have received this file from a source
# other than Hystax, then your use, modification, or distribution
# of it requires the prior written permission of Hystax.
#-------------------------------------------------------------------

echo "OptScale cleanup script for volumes_not_attached_for_a_long_time recommendations module.
Script will delete all volumes based on json file downloaded from recommendations page.
Only volumes related to cloud account ###CLOUD_ACCOUNT_NAME### which is associated with
###CLOUD_ACCOUNT_TYPE### - ###CLOUD_ACCOUNT_ACCOUNT_ID### will be deleted."

if ! command -v gcloud 1>/dev/null 2>/dev/null; then
    echo "gcloud cli is not installed"
    exit 1
fi
if ! command -v jq 1>/dev/null 2>/dev/null; then
    echo "jq is not installed"
    exit 1
fi
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <path to recommendations json>"
    exit 1
fi
if [[ ! -f $1 ]]; then
    echo "Invalid recommendations json path: $1"
    exit 1
fi

CLOUD_ACCOUNT_ID="###CLOUD_ACCOUNT_ID###"

deleted=()
failed_to_delete=()
jq -r -c '.[]' "$1" |
{
    while read row; do
        row_account_id=$(echo "${row}" | jq -r '.cloud_account_id')
        if [[ "$row_account_id" == "$CLOUD_ACCOUNT_ID" ]]; then
            name=$(echo "${row}" | jq -r '.resource_name')
            zone=$(echo "${row}" | jq -r '.zone_id')
            output=$(yes Y | gcloud compute disks delete "$name" --zone="$zone" 2>&1)
            if [[ $? -ne 0 ]]; then
                failed_to_delete+=("$name\n$output")
            else
                deleted+=("$name")
            fi
        fi
    done

    echo "Cleanup completed."

    if [[ ${#deleted[*]} -ne 0 ]]; then
        echo "Deleted volumes:"
        printf '%s\n' "${deleted[@]}"
    fi

    if [[ ${#failed_to_delete[*]} -ne 0 ]]; then
        echo "Not deleted volumes due to errors:"
        printf '\n%b\n' "${failed_to_delete[@]}"
    fi
}
