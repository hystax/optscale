#!/usr/bin/env bash
#
# OptScale EKS Cluster Preparation Script
#
# This script applies all the pre-deployment configurations that the Ansible
# playbook normally handles before running runkube.py on an EKS cluster.
#
# Usage:
#   ./prepare-eks-cluster.sh [options]
#
# Options:
#   --skip-nginx            Skip nginx-ingress installation
#   --skip-cert             Skip SSL certificate generation
#   --skip-helm-repos       Skip Helm repository setup
#   --skip-storage-dirs     Skip creating storage directories
#   --cluster-name NAME     EKS cluster name (default: auto-detect)
#   --region REGION         AWS region (default: auto-detect from kubeconfig)
#   --dry-run               Show what would be done without executing
#   --help                  Show this help message
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SKIP_NGINX=false
SKIP_CERT=false
SKIP_HELM_REPOS=false
SKIP_STORAGE_DIRS=false
CLUSTER_NAME=""
REGION=""
DRY_RUN=false

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    echo
    echo -e "${GREEN}==>${NC} ${BLUE}$*${NC}"
    echo
}

# Help message
show_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# \?//'
    exit 0
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-nginx)
                SKIP_NGINX=true
                shift
                ;;
            --skip-cert)
                SKIP_CERT=true
                shift
                ;;
            --skip-helm-repos)
                SKIP_HELM_REPOS=true
                shift
                ;;
            --skip-storage-dirs)
                SKIP_STORAGE_DIRS=true
                shift
                ;;
            --cluster-name)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log_step "Step 1: Checking Prerequisites"
    
    local missing_tools=()
    
    # Check for required tools
    for tool in kubectl helm openssl; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and try again"
        exit 1
    fi
    
    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        log_error "Please check your kubeconfig and cluster connectivity"
        exit 1
    fi
    
    # Auto-detect cluster name if not provided
    if [ -z "$CLUSTER_NAME" ]; then
        CLUSTER_NAME=$(kubectl config current-context | awk -F'/' '{print $2}' || echo "optscale-eks")
        log_info "Auto-detected cluster name: $CLUSTER_NAME"
    fi
    
    log_success "Prerequisites check passed"
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Context: $(kubectl config current-context)"
}

setup_helm_repos() {
    if $SKIP_HELM_REPOS; then
        log_info "Skipping Helm repository setup (--skip-helm-repos specified)"
        return
    fi
    
    log_step "Step 2: Setting Up Helm Repositories"
    
    if $DRY_RUN; then
        log_info "[DRY RUN] Would add Helm repositories"
        return
    fi
    
    log_info "Adding bitnami Helm repository..."
    helm repo add bitnami https://raw.githubusercontent.com/bitnami/charts/refs/heads/archive-full-index/bitnami/ || log_warn "Bitnami repo already exists"

    log_info "Adding ingress-nginx Helm repository..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx || log_warn "ingress-nginx repo already exists"

    log_info "Updating Helm repositories..."
    helm repo update

    log_success "Helm repositories configured"
}

# Generate SSL certificate
generate_ssl_cert() {
    if $SKIP_CERT; then
        log_info "Skipping SSL certificate generation (--skip-cert specified)"
        return
    fi

    log_step "Step 3: Generating Default SSL Certificate"

    # Check if certificate already exists
    if kubectl get secret defaultcert &> /dev/null; then
        log_warn "SSL certificate 'defaultcert' already exists"
        read -p "Do you want to regenerate it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipping SSL certificate generation"
            return
        fi
        kubectl delete secret defaultcert
    fi

    if $DRY_RUN; then
        log_info "[DRY RUN] Would generate SSL certificate"
        return
    fi

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT

    # Create OpenSSL config
    cat > "$temp_dir/openssl.cfg" <<EOF
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
stateOrProvinceName = Amsterdam
countryName      = NL
organizationName = Hystax BV
localityName     = Amsterdam

[ v3_req ]
basicConstraints = CA:FALSE
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.elb.amazonaws.com
DNS.3 = *.eks.amazonaws.com
IP.1 = 127.0.0.1
EOF

    log_info "Generating self-signed certificate..."
    openssl req -x509 -sha256 -nodes -newkey rsa:4096 \
        -keyout "$temp_dir/key.pem" \
        -out "$temp_dir/cert.pem" \
        -extensions v3_req \
        -days 9001 \
        -config "$temp_dir/openssl.cfg"

    log_info "Creating Kubernetes TLS secret..."
    kubectl create secret tls defaultcert \
        --key "$temp_dir/key.pem" \
        --cert "$temp_dir/cert.pem"

    log_success "SSL certificate created"
}

# Install nginx-ingress controller
install_nginx_ingress() {
    if $SKIP_NGINX; then
        log_info "Skipping nginx-ingress installation (--skip-nginx specified)"
        return
    fi

    log_step "Step 4: Installing NGINX Ingress Controller"

    # Check if nginx-ingress is already installed
    if helm list -A | grep -q "ngingress"; then
        log_warn "nginx-ingress 'ngingress' already installed"
        read -p "Do you want to upgrade it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipping nginx-ingress installation"
            return
        fi
    fi

    if $DRY_RUN; then
        log_info "[DRY RUN] Would install nginx-ingress"
        return
    fi

    # Check if custom values file exists
    local values_file="$SCRIPT_DIR/ansible/roles/k8s-configure/files/nginx-ingress/values.yaml"

    if [ -f "$values_file" ]; then
        log_info "Using custom nginx-ingress values from: $values_file"
        helm upgrade --install ngingress ingress-nginx \
            --repo https://kubernetes.github.io/ingress-nginx \
            -f "$values_file"
    else
        log_warn "Custom values file not found, using default configuration"
        log_info "Installing nginx-ingress with EKS-optimized settings..."

        # EKS-specific configuration
        helm upgrade --install ngingress ingress-nginx \
            --repo https://kubernetes.github.io/ingress-nginx \
            --set controller.service.type=LoadBalancer \
            --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"="nlb" \
            --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-cross-zone-load-balancing-enabled"="true" \
            --set controller.extraArgs.default-ssl-certificate=default/defaultcert \
            --set controller.ingressClassResource.default=true
    fi

    log_success "NGINX Ingress Controller installed"

    # Wait for LoadBalancer to be ready
    log_info "Waiting for LoadBalancer to be provisioned..."
    kubectl wait --namespace default \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s || log_warn "Timeout waiting for nginx-ingress pods"

    # Get LoadBalancer URL
    local lb_url=$(kubectl get svc ngingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
    if [ "$lb_url" != "pending" ]; then
        log_success "LoadBalancer URL: $lb_url"
        log_info "You can access OptScale at: https://$lb_url (after deployment)"
    else
        log_warn "LoadBalancer URL not yet available. Check with: kubectl get svc ngingress-ingress-nginx-controller"
    fi
}

# Create storage directories
create_storage_dirs() {
    if $SKIP_STORAGE_DIRS; then
        log_info "Skipping storage directory creation (--skip-storage-dirs specified)"
        return
    fi

    log_step "Step 5: Creating Storage Directories"

    if $DRY_RUN; then
        log_info "[DRY RUN] Would create storage directories on nodes"
        return
    fi

    log_info "Creating DaemonSet to create storage directories on all nodes..."

    # Create a DaemonSet that creates the required directories
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: optscale-storage-init
  namespace: default
spec:
  selector:
    matchLabels:
      name: optscale-storage-init
  template:
    metadata:
      labels:
        name: optscale-storage-init
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: init
        image: busybox:latest
        command:
        - sh
        - -c
        - |
          mkdir -p /host/optscale/mariadb
          mkdir -p /host/optscale/mongo
          mkdir -p /host/optscale/rabbitmq
          mkdir -p /host/optscale/etcd
          mkdir -p /host/optscale/minio
          mkdir -p /host/optscale/influxdb
          mkdir -p /host/optscale/clickhouse
          mkdir -p /host/optscale/thanos_receive
          mkdir -p /host/optscale/thanos_storegateway
          mkdir -p /host/optscale/thanos_compactor
          chmod -R 777 /host/optscale
          echo "Storage directories created successfully"
          sleep infinity
        securityContext:
          privileged: true
        volumeMounts:
        - name: host
          mountPath: /host
      volumes:
      - name: host
        hostPath:
          path: /
          type: Directory
EOF

    log_info "Waiting for storage initialization to complete..."
    sleep 10

    # Check if DaemonSet is ready
    kubectl rollout status daemonset/optscale-storage-init --timeout=120s || log_warn "Timeout waiting for storage init"

    log_success "Storage directories created on all nodes"

    # Clean up the DaemonSet
    log_info "Cleaning up initialization DaemonSet..."
    kubectl delete daemonset optscale-storage-init
}

# Configure cluster settings
configure_cluster() {
    log_step "Step 6: Configuring Cluster Settings"

    if $DRY_RUN; then
        log_info "[DRY RUN] Would configure cluster settings"
        return
    fi

    # Enable scheduling on control plane nodes (if any)
    log_info "Enabling scheduling on control plane nodes (if any)..."
    kubectl taint nodes --all node-role.kubernetes.io/control-plane- 2>/dev/null || log_info "No control plane taints to remove"
    kubectl taint nodes --all node-role.kubernetes.io/master- 2>/dev/null || log_info "No master taints to remove"

    log_success "Cluster settings configured"
}

# Display summary
show_summary() {
    log_step "Setup Complete!"

    echo -e "${GREEN}✓${NC} Prerequisites verified"

    if ! $SKIP_HELM_REPOS; then
        echo -e "${GREEN}✓${NC} Helm repositories configured"
    fi

    if ! $SKIP_CERT; then
        echo -e "${GREEN}✓${NC} SSL certificate generated"
    fi

    if ! $SKIP_NGINX; then
        echo -e "${GREEN}✓${NC} NGINX Ingress Controller installed"
    fi

    if ! $SKIP_STORAGE_DIRS; then
        echo -e "${GREEN}✓${NC} Storage directories created"
    fi

    echo -e "${GREEN}✓${NC} Cluster settings configured"

    echo
    log_info "Your EKS cluster is now ready for OptScale deployment!"
    echo
    log_info "Next steps:"
    echo "  1. Edit your overlay file: overlay/user_template.yml"
    echo "  2. Deploy OptScale:"
    echo "     ./runkube.py --with-elk -o overlay/user_template.yml -- optscale-prod"
    echo

    # Show LoadBalancer URL if available
    if ! $SKIP_NGINX && ! $DRY_RUN; then
        local lb_url=$(kubectl get svc ngingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
        if [ -n "$lb_url" ]; then
            echo -e "${BLUE}LoadBalancer URL:${NC} https://$lb_url"
            echo -e "${YELLOW}Note:${NC} Update your DNS to point to this LoadBalancer"
            echo
        fi
    fi
}

# Main execution
main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  OptScale EKS Cluster Preparation Script      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo

    parse_args "$@"
    check_prerequisites
    setup_helm_repos
    generate_ssl_cert
    install_nginx_ingress
    create_storage_dirs
    configure_cluster
    show_summary
}

# Run main function
main "$@"

