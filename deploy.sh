#!/bin/bash

# Mothership AIs Deployment Script
# This script deploys the complete Mothership AIs system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="mothership-ais"
RELEASE_NAME="mothership"
CHART_PATH="./helm"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install helm first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed. Please install docker first."
        exit 1
    fi
    
    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "All prerequisites are met"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t mothership-api:latest ./backend
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t mothership-frontend:latest ./frontend
    
    log_success "Docker images built successfully"
}

create_namespace() {
    log_info "Creating namespace..."
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace $NAMESPACE
        log_success "Namespace $NAMESPACE created"
    fi
}

deploy_with_helm() {
    log_info "Deploying with Helm..."
    
    # Add required Helm repositories
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    # Install dependencies
    helm dependency update $CHART_PATH
    
    # Deploy the application
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --create-namespace \
        --values $CHART_PATH/values.yaml \
        --wait \
        --timeout=10m
    
    log_success "Application deployed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    kubectl wait --for=condition=ready pod -l app=mothership-api -n $NAMESPACE --timeout=300s
    
    # Check services
    kubectl get services -n $NAMESPACE
    
    # Check ingress
    kubectl get ingress -n $NAMESPACE
    
    log_success "Deployment verification completed"
}

show_access_info() {
    log_info "Access Information:"
    
    echo ""
    echo "🌐 Frontend: http://mothership.local"
    echo "🔧 API: http://mothership.local/api"
    echo ""
    echo "To access locally, add this to your /etc/hosts:"
    echo "127.0.0.1 mothership.local"
    echo ""
    echo "Port forwarding commands:"
    echo "kubectl port-forward -n $NAMESPACE svc/mothership-api-service 8000:80"
    echo "kubectl port-forward -n $NAMESPACE svc/mothership-frontend-service 3000:80"
}

cleanup() {
    log_info "Cleaning up..."
    
    helm uninstall $RELEASE_NAME -n $NAMESPACE || true
    kubectl delete namespace $NAMESPACE || true
    
    log_success "Cleanup completed"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            build_images
            create_namespace
            deploy_with_helm
            verify_deployment
            show_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        "verify")
            verify_deployment
            ;;
        "info")
            show_access_info
            ;;
        *)
            echo "Usage: $0 {deploy|cleanup|verify|info}"
            echo ""
            echo "Commands:"
            echo "  deploy  - Deploy the complete Mothership AIs system"
            echo "  cleanup - Remove all deployed resources"
            echo "  verify  - Verify the deployment status"
            echo "  info    - Show access information"
            exit 1
            ;;
    esac
}

main "$@"
