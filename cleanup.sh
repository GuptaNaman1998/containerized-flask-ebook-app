#!/bin/bash

echo "=========================================="
echo "BookApp GCP Cleanup Script"
echo "=========================================="
echo ""

# Set project
export DEV_PROJECT=$DEVSHELL_PROJECT_ID
gcloud config set project $DEV_PROJECT

echo "Project: $DEV_PROJECT"
echo ""

# Get current region and zone from gcloud config or cluster
echo "Detecting cluster location..."
CLUSTER_INFO=$(gcloud container clusters list --filter="name=bookapp-cluster" --format="value(location)" 2>/dev/null)

if [ -n "$CLUSTER_INFO" ]; then
    if [[ $CLUSTER_INFO == *"-"*"-"* ]]; then
        # It's a zone (e.g., us-central1-a)
        export zone=$CLUSTER_INFO
        export region=${zone%-*}
    else
        # It's a region (e.g., us-central1)
        export region=$CLUSTER_INFO
        export zone=""
    fi
    echo "Found cluster in: $CLUSTER_INFO"
else
    echo "No cluster found, using default region us-central1"
    export region="us-central1"
    export zone="us-central1-a"
fi

echo ""
echo "=========================================="
echo "WARNING: This will delete ALL resources!"
echo "=========================================="
echo "The following resources will be deleted:"
echo "- Kubernetes cluster: bookapp-cluster"
echo "- Docker images in Artifact Registry: bookapp-repo"
echo "- Artifact Registry repository: bookapp-repo"
echo ""

read -p "Are you sure you want to proceed? (yes/no): " confirm

if [[ $confirm != "yes" && $confirm != "y" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup process..."
echo ""

# Step 1: Delete Kubernetes deployments and services
echo "1. Deleting Kubernetes deployments and services..."
kubectl delete deployment bookapp-web bookapp-db bookapp-pgladmin 2>/dev/null || echo "   Some deployments may not exist"
kubectl delete service bookapp-web bookapp-db bookapp-pgladmin 2>/dev/null || echo "   Some services may not exist"
echo "   ✓ Kubernetes resources deleted"

# Step 2: Delete the GKE cluster
echo ""
echo "2. Deleting GKE cluster..."
if [ -n "$zone" ]; then
    echo "   Deleting zonal cluster in zone: $zone"
    gcloud container clusters delete bookapp-cluster \
        --zone=$zone \
        --quiet
else
    echo "   Deleting regional cluster in region: $region"
    gcloud container clusters delete bookapp-cluster \
        --region=$region \
        --quiet
fi
echo "   ✓ GKE cluster deleted"

# Step 3: Delete Docker images from Artifact Registry
echo ""
echo "3. Deleting Docker images from Artifact Registry..."
echo "   Deleting bookapp_web image..."
gcloud artifacts docker images delete $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_web --quiet 2>/dev/null || echo "   Image may not exist"

echo "   Deleting bookapp_db image..."
gcloud artifacts docker images delete $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_db --quiet 2>/dev/null || echo "   Image may not exist"

echo "   Deleting bookapp_pgladmin image..."
gcloud artifacts docker images delete $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_pgladmin --quiet 2>/dev/null || echo "   Image may not exist"

echo "   ✓ Docker images deleted"

# Step 4: Delete the Artifact Registry repository
echo ""
echo "4. Deleting Artifact Registry repository..."
gcloud artifacts repositories delete bookapp-repo \
    --location=$region \
    --quiet
echo "   ✓ Artifact Registry repository deleted"

# Step 5: Clean up local Docker authentication (optional)
echo ""
echo "5. Cleaning up local Docker configuration..."
# Remove the specific registry from Docker config (optional, doesn't affect billing)
if command -v docker &> /dev/null; then
    echo "   Removing Docker authentication for $region-docker.pkg.dev"
    # This is optional and won't affect GCP billing
    docker logout $region-docker.pkg.dev 2>/dev/null || echo "   No local Docker auth to clean"
fi
echo "   ✓ Local cleanup completed"

echo ""
echo "=========================================="
echo "✅ Cleanup completed successfully!"
echo "=========================================="
echo ""
echo "All BookApp resources have been deleted:"
echo "- GKE cluster: bookapp-cluster"
echo "- Docker images: bookapp_web, bookapp_db, bookapp_pgladmin"
echo "- Artifact Registry repository: bookapp-repo"
echo ""
echo "Your GCP project is now clean of BookApp resources."
echo "No further charges should accrue from these resources."
