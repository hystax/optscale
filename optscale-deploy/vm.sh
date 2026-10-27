#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

STATE_DIR="$SCRIPT_DIR/.vagrant/.vm-state"
PROVIDER_FILE="$STATE_DIR/provider"
ARCH_FILE="$STATE_DIR/arch"
CPUS_FILE="$STATE_DIR/cpus"
RAM_FILE="$STATE_DIR/ram_gb"
DISK_FILE="$STATE_DIR/disk_gb"

_save_state_kv() {
    local file="$1"
    local val="$2"
    mkdir -p "$STATE_DIR"
    printf '%s\n' "$val" > "$file"
}

_load_state_kv() {
    local file="$1"
    if [[ -f "$file" ]]; then
        cat "$file"
    else
        echo ""
    fi
}

save_cpus() { _save_state_kv "$CPUS_FILE" "$1"; }
load_cpus() { _load_state_kv "$CPUS_FILE"; }

save_ram_gb() { _save_state_kv "$RAM_FILE" "$1"; }
load_ram_gb() { _load_state_kv "$RAM_FILE"; }

save_disk_gb() { _save_state_kv "$DISK_FILE" "$1"; }
load_disk_gb() { _load_state_kv "$DISK_FILE"; }


save_provider() {
    mkdir -p "$STATE_DIR"
    printf '%s\n' "$1" > "$PROVIDER_FILE"
}

load_provider() {
    if [[ -f "$PROVIDER_FILE" ]]; then
        cat "$PROVIDER_FILE"
    else
        echo ""
    fi
}

save_arch() {
    mkdir -p "$STATE_DIR"
    printf '%s\n' "$1" > "$ARCH_FILE"
}

load_arch() {
    if [[ -f "$ARCH_FILE" ]]; then
        cat "$ARCH_FILE"
    else
        echo ""
    fi
}

clear_state() {
    rm -rf "$STATE_DIR"
}


function host_arch_family {
    local host_arch
    host_arch="$(uname -m)"

    case "$host_arch" in
        x86_64|amd64) echo "x86" ;;
        aarch64|arm64) echo "arm" ;;
        *)
            echo "Error: Unsupported host architecture '$host_arch'." >&2
            exit 1
            ;;
    esac
}

function arch_is_suitable {
    local requested="$1"
    local host
    host="$(host_arch_family)"

    [[ "$requested" == "$host" ]]
}

print_help() {
    cat <<EOF
usage: $0 [x86|arm] [--provider <qemu|virtualbox>] [--no-thanos] <command> [<args>...]

Available commands:
    info             show vm status and info
    optscale-info    show optscale cluster info
    start, up        start the vm
    stop, down       stop the vm
    destroy          destroy the vm
    restart          stop and start the vm
    reset            destroy and start the vm
    ssh              ssh into the vm
    playbook         run an ansible playbook
    role             run an ansible role
    deploy-service   deploy a service inside the vm
    update-only      rebuild images and update existing optscale release

Global options:
    --provider qemu|virtualbox  force specific Vagrant provider
    --allow-emulation           allow starting non-native architecture VM (emulation)
    --cpus N                    set VM vCPUs (default: 4)
    --ram N                     set VM RAM in GB (default: 10)
    --disk N                    set VM disk size in GB (default: 75)
    --no-thanos                 disable thanos components (passed to ansible & runkube)
    --with-elk                  enable ELK stack (build elk image, pass --with-elk to runkube)
    --help, -h                  show this help message

EOF
}

# check if --help or -h is passed as any argument regardless of its position
if [[ "$@" == *"--help"* || "$@" == *"-h"* ]]; then
    print_help
    exit 0
fi

ALLOW_EMULATION=0
PROVIDER=""
DISABLE_THANOS=0
WITH_ELK=0
CPUS=""
RAM_GB=""
DISK_GB=""

args=("$@")
clean_args=()

i=0
while [[ $i -lt $# ]]; do
    arg="${args[$i]}"

    case "$arg" in
        --provider)
            # next arg must contain provider
            if [[ $((i+1)) -ge $# ]]; then
                echo "Error: --provider must be followed by qemu or virtualbox"
                exit 1
            fi
            PROVIDER="${args[$((i+1))]}"
            i=$((i+2))
            continue
            ;;
        --provider=*)
            PROVIDER="${arg#*=}"
            i=$((i+1))
            continue
            ;;
        --allow-emulation)
            ALLOW_EMULATION=1
            i=$((i+1))
            continue
            ;;
        --no-thanos|--disable-thanos)
            DISABLE_THANOS=1
            i=$((i+1))
            continue
            ;;
        --cpus)
            if [[ $((i+1)) -ge $# ]]; then
                echo "Error: --cpus must be followed by a number"
                exit 1
            fi
            CPUS="${args[$((i+1))]}"
            i=$((i+2))
            continue
            ;;
        --cpus=*)
            CPUS="${arg#*=}"
            i=$((i+1))
            continue
            ;;
        --ram)
            if [[ $((i+1)) -ge $# ]]; then
                echo "Error: --ram must be followed by a number (GB)"
                exit 1
            fi
            RAM_GB="${args[$((i+1))]}"
            i=$((i+2))
            continue
            ;;
        --ram=*)
            RAM_GB="${arg#*=}"
            i=$((i+1))
            continue
            ;;
        --disk)
            if [[ $((i+1)) -ge $# ]]; then
                echo "Error: --disk must be followed by a number (GB)"
                exit 1
            fi
            DISK_GB="${args[$((i+1))]}"
            i=$((i+2))
            continue
            ;;
        --with-elk|--elk)
            WITH_ELK=1
            i=$((i+1))
            continue
            ;;
        --disk=*)
            DISK_GB="${arg#*=}"
            i=$((i+1))
            continue
            ;;
        *)
            clean_args+=("$arg")
            ;;
    esac

    i=$((i+1))
done

# Normalize provider if given; otherwise reuse the last selected provider
if [[ "$PROVIDER" == "qemu" || "$PROVIDER" == "virtualbox" ]]; then
    export VAGRANT_DEFAULT_PROVIDER="$PROVIDER"
    save_provider "$PROVIDER"
elif [[ -n "$PROVIDER" ]]; then
    echo "Error: unsupported provider '$PROVIDER'. Expected 'qemu' or 'virtualbox'."
    exit 1
else
    last_provider="$(load_provider)"
    if [[ -n "$last_provider" ]]; then
        export VAGRANT_DEFAULT_PROVIDER="$last_provider"
    fi
fi

if [[ -z "${VAGRANT_DEFAULT_PROVIDER:-}" ]]; then
    export VAGRANT_DEFAULT_PROVIDER="qemu"
    save_provider "qemu"
fi

EFFECTIVE_CPUS=""
EFFECTIVE_RAM_GB=""
EFFECTIVE_DISK_GB=""

if [[ -n "$CPUS" ]]; then
    EFFECTIVE_CPUS="$CPUS"
    save_cpus "$EFFECTIVE_CPUS"
else
    EFFECTIVE_CPUS="$(load_cpus)"
fi

if [[ -n "$RAM_GB" ]]; then
    EFFECTIVE_RAM_GB="$RAM_GB"
    save_ram_gb "$EFFECTIVE_RAM_GB"
else
    EFFECTIVE_RAM_GB="$(load_ram_gb)"
fi

if [[ -n "$DISK_GB" ]]; then
    EFFECTIVE_DISK_GB="$DISK_GB"
    save_disk_gb "$EFFECTIVE_DISK_GB"
else
    EFFECTIVE_DISK_GB="$(load_disk_gb)"
fi

# Export only if we actually have values
if [[ -n "$EFFECTIVE_CPUS" ]]; then
    export VM_CPUS="$EFFECTIVE_CPUS"
fi

if [[ -n "$EFFECTIVE_RAM_GB" ]]; then
    export VM_RAM_GB="$EFFECTIVE_RAM_GB"
fi

if [[ -n "$EFFECTIVE_DISK_GB" ]]; then
    export VM_DISK_GB="$EFFECTIVE_DISK_GB"
fi

# Replace original args with cleaned ones
set -- "${clean_args[@]}"

if [[ $# -lt 1 ]]; then
    echo "Error: Invalid number of arguments."
    print_help
    exit 1
fi

if [[ "${1:-}" == "x86" || "${1:-}" == "arm" ]]; then
    COMMAND_PEEK="${2:-}"
else
    COMMAND_PEEK="${1:-}"
fi

if [[ -z "${COMMAND_PEEK:-}" ]]; then
    echo "Error: Missing command."
    print_help
    exit 1
fi

if [[ "$1" == "x86" || "$1" == "arm" ]]; then
    VM_ARCH="$1"

    if arch_is_suitable "$VM_ARCH"; then
        save_arch "$VM_ARCH"
    else
        if [[ "$COMMAND_PEEK" == "destroy" || "$COMMAND_PEEK" == "stop" || "$COMMAND_PEEK" == "down" ]]; then
            echo "Warning: '$VM_ARCH' is not suitable for this host ($(uname -m)), but allowing '$COMMAND_PEEK'."
            echo "Arch will NOT be saved."
        elif [[ "${ALLOW_EMULATION:-0}" -eq 1 ]]; then
            export ALLOW_EMULATION
            echo "Warning: '$VM_ARCH' is not native for this host ($(uname -m)), but --allow-emulation is set."
            echo "Arch will NOT be saved."
        else
            echo "Error: '$VM_ARCH' is not suitable for this host ($(uname -m))."
            echo "Hint: add --allow-emulation to run non-native architecture VM."
            echo "Tip: use the native arch or run 'destroy'/'stop' to clean up that VM."
            exit 2
        fi
    fi

    shift
else
    last_arch="$(load_arch)"
    if [[ -n "$last_arch" ]]; then
        VM_ARCH="$last_arch"
        echo "VM architecture not provided, using saved: $VM_ARCH"
    else
        host_os_arch=$(uname -m)
        if [[ "$host_os_arch" == "x86_64" || "$host_os_arch" == "amd64" ]]; then
            VM_ARCH="x86"
        elif [[ "$host_os_arch" == "aarch64" || "$host_os_arch" == "arm64" ]]; then
            VM_ARCH="arm"
        else
            echo "Error: Unsupported host architecture '$host_os_arch'. Provide 'x86' or 'arm'."
            exit 1
        fi
        save_arch "$VM_ARCH"
        echo "VM architecture not provided, using host: $VM_ARCH"
    fi
fi



COMMAND="$1"
shift

if [[ "$VM_ARCH" == "x86" ]]; then
    VM_NAME="ubuntu-2404-x86-64"
else
    VM_NAME="ubuntu-2404-arm-64"
fi

INVENTORY_FILE="$SCRIPT_DIR/ansible/inventories/vm-$VM_ARCH.yaml"

function require_arch_compatible_or_die {
    local cmd="$1"
    case "$cmd" in
        start|up|restart|reset) ;;
        *) return 0 ;;
    esac

    local host_arch
    host_arch="$(uname -m)"

    local host_family=""
    case "$host_arch" in
        x86_64|amd64) host_family="x86" ;;
        aarch64|arm64) host_family="arm" ;;
        *)
            echo "Error: Unsupported host architecture '$host_arch'."
            exit 1
            ;;
    esac

    if [[ "$VM_ARCH" != "$host_family" ]]; then
        if [[ "${ALLOW_EMULATION:-0}" -eq 1 ]]; then
            echo "Warning: starting '$VM_ARCH' VM on '$host_arch' host (non-native), because --allow-emulation is set."
            return 0
        fi

        echo "Error: You're trying to start '$VM_ARCH' VM on '$host_arch' host."
        echo "This script is configured to fail-fast on non-native architecture."
        echo
        echo "Fix: run with the native arch:"
        echo
        echo "Hint: add --allow-emulation to run non-native architecture VM (at own risk)"

        if [[ "$host_family" == "x86" ]]; then
            echo "  $0 x86 --provider ${VAGRANT_DEFAULT_PROVIDER} up"
        else
            echo "  $0 arm --provider ${VAGRANT_DEFAULT_PROVIDER} up"
        fi
        exit 2
    fi
}

function _venv_run {
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        exec "$@"
    elif type uv >/dev/null 2>&1; then
        uv run --directory "$SCRIPT_DIR" "$@"
    else
        default_venv_dir="$SCRIPT_DIR/.venv"
        if [[ ! -d "$default_venv_dir" ]]; then
            echo "Error: No virtualenv found."
            exit 1
        fi
        exec "$default_venv_dir/bin/$@"
    fi
}

function vm_info {
    vm_state=$(vagrant status $VM_NAME --machine-readable | grep ',state,' | cut -d ',' -f4)
    vm_qemu_id=$(cat ".vagrant/machines/$VM_NAME/qemu/id" 2>/dev/null || echo "")
    vm_vagrant_id=$(cat ".vagrant/machines/$VM_NAME/qemu/index_uuid" 2>/dev/null || echo "")

    vm_process_info=$(ps -eo pid,command | grep "qemu-system-.*$VM_NAME" | grep -v grep || echo "")
    vm_qemu_pid=$(echo "$vm_process_info" | cut -d ' ' -f1 || echo "")
    vm_qemu_accelerator=$(echo "$vm_process_info" | sed 's/.*-accel \([^ ]*\).*/\1/' || echo "")

    echo "Name:             ${VM_NAME}"
    echo "State:            ${vm_state:-unknown}"
    echo "QEMU Machine ID:  ${vm_qemu_id:-N/A}"
    echo "Vagrant ID:       ${vm_vagrant_id:-N/A}"
    echo "QEMU Process ID:  ${vm_qemu_pid:-N/A}"
    echo "QEMU Accelerator: ${vm_qemu_accelerator:-N/A}"
    echo "VM_CPUS:          ${VM_CPUS:-$(load_cpus):-default}"
    echo "VM_RAM_GB:        ${VM_RAM_GB:-$(load_ram_gb):-default}"
    echo "VM_DISK_GB:       ${VM_DISK_GB:-$(load_disk_gb):-default}"
}

function vm_start {
    vagrant up $VM_NAME
}

function vm_stop {
    vagrant halt $VM_NAME "$@"

    if [[ "$@" == *"--force"* ]]; then
        pid=$(pgrep -f "qemu-system-.*$VM_NAME" || true)
        [[ -n "$pid" ]] && kill "$pid"
    fi

    while pgrep -f "qemu-system-.*$VM_NAME" >/dev/null; do
        echo "$(date +%X) - Waiting until VM stops"
        sleep 1
    done
}

function vm_destroy {
    vm_stop --force
    vagrant destroy --force $VM_NAME
    clear_state
}

function vm_ssh {
    cmd_to_run="${1:-/bin/bash}"

    if [[ "$TERM" == "xterm-kitty" ]]; then
        TERM="xterm-256color" vagrant ssh $VM_NAME -c "$cmd_to_run"
    else
        vagrant ssh $VM_NAME -c "$cmd_to_run"
    fi
}

function vm_run_ansible_playbook {
    local playbook="$1"
    shift

    if [[ -f "$playbook" ]]; then
        playbook_path="$playbook"
    elif [[ -f "$SCRIPT_DIR/ansible/$playbook.yaml" ]]; then
        playbook_path="$SCRIPT_DIR/ansible/$playbook.yaml"
    else
        echo "Error: playbook '$playbook' not found."
        exit 1
    fi

    extra_vars=()
    if [[ "$DISABLE_THANOS" -eq 1 ]]; then
        extra_vars+=(-e disable_thanos=true)
    fi
    if [[ "$WITH_ELK" -eq 1 ]]; then
        extra_vars+=(-e with_elk=true)
    fi

    _venv_run ansible-playbook --inventory-file "$INVENTORY_FILE" \
        "${extra_vars[@]}" \
        "$playbook_path" "$@"
}


function vm_run_ansible_role {
    local role="$1"
    shift

    if [[ -d "$SCRIPT_DIR/ansible/roles/$role" ]]; then
        role_path="$SCRIPT_DIR/ansible/roles/$role"
    else
        echo "Error: role '$role' not found."
        exit 1
    fi

    _venv_run ansible all \
        --inventory-file "$INVENTORY_FILE" \
        --module-name include_role \
        --args "name=$role_path" \
        "$@"
}

function vm_show_optscale_info {
    cluster_secret=$(vm_ssh "kubectl get secret cluster-secret -o jsonpath='{.data.cluster_secret}' | base64 --decode; echo")
    cluster_ip_addr=$(vm_ssh "kubectl get svc ngingress-ingress-nginx-controller -o jsonpath='{.spec.clusterIP}'")

    forwarded_https_port=$(grep -A10 "define_vm" "$SCRIPT_DIR/Vagrantfile" |
        grep -A10 "$VM_NAME" |
        grep -o "https: [0-9]*" |
        awk '{print $2}')

    frontend_url="https://localhost:$forwarded_https_port/"
    status_code=$(curl --insecure -L -I "$frontend_url" -sw '%{http_code}\n' -o /dev/null || echo "")

    echo "Frontend URL: $frontend_url [$status_code]"
    echo "Cluster IP Address: $cluster_ip_addr"
    echo "Cluster Secret: $cluster_secret"

    k8s_pods=$(vm_ssh "kubectl get pods --all-namespaces")
    echo "================================"
    echo "K8S Pods"
    echo "$k8s_pods"
}

function vm_deploy_service {
    vagrant rsync "$VM_NAME"

    if [[ $# -eq 1 ]]; then
        service_name="$1"
        vm_ssh "cd optscale && ./build.sh --use-nerdctl $service_name local"
    fi

    # Build overlay args for runkube
    local overlay_args="-o overlay/user_template.yml"
    if [[ "$DISABLE_THANOS" -eq 1 ]]; then
        overlay_args="$overlay_args overlay/user_thanos_disabled.yml"
    fi

    local elk_flag=""
    if [[ "$WITH_ELK" -eq 1 ]]; then
        elk_flag="--with-elk"
    fi

    vm_ssh "cd optscale/optscale-deploy && .venv/bin/python runkube.py --no-pull $elk_flag $overlay_args -- optscale local"
}

function vm_update_only {
    # Find running OptScale release based on chart/name containing "optscale"
    local releases release_name

    releases=$(vm_ssh "helm list -o json 2>/dev/null | python3 -c 'import sys, json; data = json.load(sys.stdin); print(\"\\n\".join(r[\"name\"] for r in data if \"optscale\" in r.get(\"chart\", \"\") or \"optscale\" in r.get(\"name\", \"\")))' || true")
    releases=$(echo "$releases" | sed '/^$/d')

    if [[ -z "$releases" ]]; then
        echo "Error: No running OptScale release with chart/name containing 'optscale' found."
        echo "helm list output from VM:"
        vm_ssh "helm list 2>/dev/null || true"
        exit 1
    fi

    if [[ $(echo "$releases" | wc -l) -ne 1 ]]; then
        echo "Error: Multiple OptScale-like releases found:"
        echo "$releases"
        echo "Please clean up or update the script to select one."
        exit 1
    fi

    release_name=$(echo "$releases" | head -n1 | tr -d '\r\n')
    echo "Using OptScale release: ${release_name}"

    # Rebuild services (all or specific)
    if [[ $# -eq 0 ]]; then
        echo "Rebuilding all OptScale images inside VM..."
        vm_ssh "cd optscale && ./build.sh --use-nerdctl"
    else
        for svc in "$@"; do
            echo "Rebuilding service: ${svc}"
            vm_ssh "cd optscale && ./build.sh --use-nerdctl ${svc} local"
        done
    fi

    local elk_flag=""
    if [[ "$WITH_ELK" -eq 1 ]]; then
        elk_flag="--with-elk"
    fi

    echo "Running runkube update-only for release '${release_name}'..."
    vm_ssh "cd optscale/optscale-deploy && .venv/bin/python runkube.py --update-only --no-pull $elk_flag -- ${release_name} local"
}

require_arch_compatible_or_die "$COMMAND"
case $COMMAND in
    info) vm_info ;;
    optscale-info) vm_show_optscale_info ;;
    start|up) vm_start ;;
    stop|down) vm_stop "$@" ;;
    destroy) vm_destroy ;;
    restart) vm_stop; vm_start ;;
    reset) vm_destroy; vm_start ;;
    ssh) vm_ssh "$@" ;;
    playbook) vm_run_ansible_playbook "$@" ;;
    role) vm_run_ansible_role "$@" ;;
    deploy-service) vm_deploy_service "$@" ;;
    update-only) vm_update_only "$@" ;;
    *)
        echo "Error: Invalid command: $COMMAND"
        print_help
        exit 1
        ;;
esac
