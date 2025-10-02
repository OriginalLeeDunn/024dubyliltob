# Oracle Cloud Kubernetes Setup Guide

## After Your Cluster is Created

### Step 1: Access Your Cluster
1. Go to Oracle Cloud Console → Developer Services → Kubernetes Clusters (OKE)
2. Click on your cluster name (`lilybud420-cluster`)
3. Click "Access Cluster" button
4. Follow the instructions to install `oci` CLI and download kubeconfig

### Step 2: Install OCI CLI (if needed)
```bash
# On Linux/Mac
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Follow prompts to configure with your Oracle Cloud credentials
```

### Step 3: Download Kubeconfig
```bash
# Replace with your actual values from Oracle Cloud Console
oci ce cluster create-kubeconfig \
  --cluster-id <your-cluster-ocid> \
  --file $HOME/.kube/config \
  --region <your-region> \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT
```

### Step 4: Test Connection
```bash
kubectl get nodes
```

### Step 5: Create GitHub Secret
```bash
# Convert kubeconfig to base64
cat ~/.kube/config | base64 -w0

# Copy the output and add it as KUBECONFIG_B64 secret in GitHub repo settings
```

## GitHub Secrets Setup

Go to: `https://github.com/OriginalLeeDunn/024dubyliltob/settings/secrets/actions`

Add these secrets:
- `KUBECONFIG_B64` - The base64 encoded kubeconfig from above
- `HIGHRISE_BOT_TOKEN` - Your bot token (regenerate the exposed one!)
- `HIGHRISE_ROOM_ID` - `6884b2c275d22eb7f880c2cd`
- `HIGHRISE_API_KEY` - Your API key (optional)

## Deploy Your Bot

### Option 1: Manual Deploy
```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl -n lilybud420 create secret generic lilybud420-secrets \
  --from-literal=HIGHRISE_BOT_TOKEN="your_new_token" \
  --from-literal=HIGHRISE_ROOM_ID="6884b2c275d22eb7f880c2cd" \
  --from-literal=HIGHRISE_API_KEY="your_api_key"

# Deploy bot
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl -n lilybud420 get pods
kubectl -n lilybud420 logs -f deployment/lilybud420-bot
```

### Option 2: GitHub Actions Deploy
1. Push any change to trigger the build
2. Go to Actions → Build and Deploy → Run workflow
3. Set `deploy` to `true`
4. Click "Run workflow"

## Troubleshooting

### Check Pod Status
```bash
kubectl -n lilybud420 get pods
kubectl -n lilybud420 describe pod <pod-name>
kubectl -n lilybud420 logs <pod-name>
```

### Check Secrets
```bash
kubectl -n lilybud420 get secrets
kubectl -n lilybud420 describe secret lilybud420-secrets
```

### Update Bot Image
```bash
kubectl -n lilybud420 rollout restart deployment/lilybud420-bot
```
