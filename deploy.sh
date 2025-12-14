gcloud auth login
export DEV_PROJECT=$DEVSHELL_PROJECT_ID
gcloud config set project $DEV_PROJECT

# Interactive region and zone selection
declare -A regions=(["us-central1"]="Iowa:a,b,c,f" ["us-east1"]="South Carolina:b,c,d" ["us-east4"]="Northern Virginia:a,b,c" ["us-west1"]="Oregon:a,b,c" ["us-west2"]="Los Angeles:a,b,c" ["europe-west1"]="Belgium:b,c,d" ["asia-southeast1"]="Singapore:a,b,c")

echo "Available regions and zones:"
region_keys=(us-central1 us-east1 us-east4 us-west1 us-west2 europe-west1 asia-southeast1)
for i in "${!region_keys[@]}"; do
    region="${region_keys[i]}"
    zones="${regions[$region]#*:}"
    echo "$((i+1)). $region (${regions[$region]%%:*}) - zones: ${zones//,/}"
done
echo "Format: [region#][zone] (e.g., 1a, 2c) or 'custom' for custom region:zone"

read -p "Select: " choice
if [[ $choice =~ ^[1-7][a-z]$ ]]; then
    region_num="${choice%?}"; zone_letter="${choice: -1}"
    export region="${region_keys[$((region_num-1))]}"
    if [[ "${regions[$region]#*:}" == *"$zone_letter"* ]]; then
        export zone="$region-$zone_letter"
    else
        zones=(${regions[$region]#*:}); export zone="$region-${zones[0]//,/}"
        echo "Invalid zone. Using $zone"
    fi
elif [[ $choice == "custom" ]]; then
    read -p "Enter region:zone: " custom; export region="${custom%:*}" zone="${custom#*:}"
else
    echo "Invalid. Using us-east1-b"; export region="us-east1" zone="us-east1-b"
fi

echo ""
echo "Selected region: $region"
echo "Selected zone: $zone"
echo "Project: $DEV_PROJECT"
echo ""

# Update YAML files with correct region and project ID before building
sed -i "s/us-central1-docker.pkg.dev/${region}-docker.pkg.dev/g" *.yaml
sed -i "s/qwiklabs-gcp-00-89a63ec84c86/${DEV_PROJECT}/g" *.yaml

gcloud artifacts repositories create bookapp-repo \
    --repository-format=docker \
    --location=$region \
    --description="Docker repository for Book App"
docker build -t $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_db ./bookapp_db --no-cache
docker build -t $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_web ./bookapp_web --no-cache
docker build -t $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_pgadmin ./bookapp_pgadmin --no-cache
docker push $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_db
docker push $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_web
docker push $region-docker.pkg.dev/$DEV_PROJECT/bookapp-repo/bookapp_pgadmin
gcloud container clusters create bookapp-cluster \
    --num-nodes=2 \
    --zone=$zone
gcloud container clusters get-credentials bookapp-cluster --zone=$zone
kubectl apply -f bookapp_db-deployment.yaml
kubectl apply -f bookapp_web-deployment.yaml
kubectl apply -f bookapp_pgadmin-deployment.yaml
kubectl get services -o jsonpath='{range .items[*]}{.metadata.namespace}{"/"}{.metadata.name}{" -> http://"}{.status.loadBalancer.ingress[0].ip}{"\n"}{end}'
