#!/usr/bin/env bash
#-------------------------------------------------------------------
# Hystax
# Copyright 2016-###YEAR### Hystax
# All Rights Reserved
#
# NOTICE:  Hystax permits you to use this file in accordance
# with the terms of the Hystax license agreement
# accompanying it.  If you have received this file from a source
# other than Hystax, then your use, modification, or distribution
# of it requires the prior written permission of Hystax.
#-------------------------------------------------------------------

echo "OptScale cleanup script for instances_in_stopped_state_for_a_long_time recommendations module.
Script will deallocate all instances based on json file downloaded from recommendations page.
Only instances related to cloud account ###CLOUD_ACCOUNT_NAME### which is associated with
###CLOUD_ACCOUNT_TYPE### - ###CLOUD_ACCOUNT_ACCOUNT_ID### will be deallocated."

if ! command -v az 1>/dev/null 2>/dev/null; then
    echo "azure cli is not installed"
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

deallocated=()
failed_to_deallocate=()
not_found_or_skipped=()
jq -r -c '.[]' "$1" |
{
    while read row; do
        row_account_id=$(echo "${row}" | jq -r '.cloud_account_id')
        if [[ "$row_account_id" == "$CLOUD_ACCOUNT_ID" ]]; then
            vm_id=$(echo "${row}" | jq -r '.cloud_resource_id')
            vm_status=$(az vm get-instance-view --query instanceView.statuses[1].code --ids "$vm_id" 2>&1)
            if [[ $vm_status =~ "PowerState/stopped" ]]; then
                output=$(az vm deallocate --ids "$vm_id" 2>&1)
                if [[ $? -ne 0 ]]; then
                    failed_to_deallocate+=("$vm_id\n$output")
                else
                    deallocated+=("$vm_id")
                fi
            else
                not_found_or_skipped+=("$vm_id\n$vm_status")
            fi
        fi
    done

    echo "Cleanup completed."

    if [[ ${#deallocated[*]} -ne 0 ]]; then
        echo "Deallocated vms:"
        printf '%s\n' "${deallocated[@]}"
    fi

    if [[ ${#failed_to_deallocate[*]} -ne 0 ]]; then
        echo "Not deallocated vms due to errors:"
        printf '\n%b\n' "${failed_to_deallocate[@]}"
    fi

    if [[ ${#not_found_or_skipped[*]} -ne 0 ]]; then
        echo "Not found vms or skipped due wrong state:"
        printf '\n%b\n' "${not_found_or_skipped[@]}"
    fi
}
