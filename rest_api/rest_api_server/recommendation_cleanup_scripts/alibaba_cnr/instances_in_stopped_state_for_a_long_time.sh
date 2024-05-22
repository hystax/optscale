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
Script will switch to StopCharging all instances based on json file downloaded from recommendations page.
Only instances related to cloud account ###CLOUD_ACCOUNT_NAME### which is associated with
###CLOUD_ACCOUNT_TYPE### - ###CLOUD_ACCOUNT_ACCOUNT_ID### will be switched to StopCharging."

if ! command -v aliyun 1>/dev/null 2>/dev/null; then
    echo "Alibaba Cloud cli is not installed"
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
    regions_json=$(aliyun ecs DescribeRegions --AcceptLanguage 'en-US' 2>&1)
    while read row; do
        row_account_id=$(echo "${row}" | jq -r '.cloud_account_id')
        if [[ "$row_account_id" == "$CLOUD_ACCOUNT_ID" ]]; then
            region_name=$(echo "${row}" | jq -r '.region')
            region_id=$(echo "$regions_json" | jq -r ".Regions.Region[] | select(.LocalName==\"$region_name\") | .RegionId" 2>&1)
            vm_id=$(echo "${row}" | jq -r '.cloud_resource_id')
            vm_info_json=$(aliyun --region "$region_id" ecs DescribeInstances --InstanceIds "[\"$vm_id\"]" 2>&1)
            vm_status=$(echo "$vm_info_json" | jq -r '.Instances.Instance[0].Status')
            vm_stopped_mode=$(echo "$vm_info_json" | jq -r '.Instances.Instance[0].StoppedMode')
            if [[ $vm_status = "Stopped" ]] && [[ $vm_stopped_mode = "KeepCharging" ]]; then
                output=$(aliyun --region "$region_id" ecs StopInstances --StoppedMode StopCharging --InstanceId.1 "$vm_id" 2>&1)
                if [[ $? -ne 0 ]]; then
                    failed_to_deallocate+=("$vm_id\n$output")
                else
                    deallocated+=("$vm_id")
                fi
            else
                not_found_or_skipped+=("$vm_id\n$vm_status/$vm_stopped_mode")
            fi
        fi
    done

    echo "Cleanup completed."

    if [[ ${#deallocated[*]} -ne 0 ]]; then
        echo "VMs switched to StopCharging:"
        printf '%s\n' "${deallocated[@]}"
    fi

    if [[ ${#failed_to_deallocate[*]} -ne 0 ]]; then
        echo "VMs not switched to StopCharging due to errors:"
        printf '\n%b\n' "${failed_to_deallocate[@]}"
    fi

    if [[ ${#not_found_or_skipped[*]} -ne 0 ]]; then
        echo "Not found VMs or skipped due wrong Status/StoppedMode:"
        printf '\n%b\n' "${not_found_or_skipped[@]}"
    fi
}
