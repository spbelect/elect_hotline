# Production deployment

System checks can help to detect common configuration tasks:

```
python manage.py check --tag email --deploy
python manage.py check --deploy --fail-level=WARNING && DJANGO_DEBUG=0 gunicorn "wsgi:application" --access-logfile - --workers 12 --threads 12 --reload
```


## Kubernetes

If you have kubeconfig for your cluster, enable it with
`export KUBECONFIG=./third-space-kubeconfig.yml`


### Create namespace

```
kubectl create namespace "ufo-ns"

kubectl config set-context --current --namespace=ufo-ns
```


### Install gateway-api

```
kubectl apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.1/standard-install.yaml
kubectl apply -f https://raw.githubusercontent.com/nginx/nginx-gateway-fabric/v1.5.1/deploy/crds.yaml
kubectl apply -f https://raw.githubusercontent.com/nginx/nginx-gateway-fabric/v1.5.1/deploy/nodeport/deploy.yaml
```


### Create secrets

```
read -p "postgres password: " password && kubectl create secret generic postgres-secrets --namespace "ufo-ns" --from-literal POSTGRES_PASSWORD="$password" --from-literal DATABASE_URL="postgresql://pguser:$password@postgres:5432/pgdb"

kubectl create secret generic ufo-secret-key --namespace "ufo-ns" --from-literal DJANGO_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1`

kubectl delete secret ufo-secrets --ignore-not-found && read -p "GOOGLE_OAUTH2_CLIENT_SECRET: " google_secret && kubectl create secret generic ufo-secrets --namespace "ufo-ns" --from-literal GOOGLE_OAUTH2_CLIENT_SECRET="$google_secret"

kubectl delete secret sendgrid-secrets --ignore-not-found && read -p "SENDGRID_API_KEY: " sendgrid_api_key && kubectl create secret generic sendgrid-secrets --namespace "ufo-ns" --from-literal SENDGRID_API_KEY="$sendgrid_api_key"

```

### Create env configmap

`cp src/env-local.example env-kube`

Edit `env-kube` file to set required environment variables. Then apply:

`kubectl create configmap ufo-config --from-env-file env-kube -o yaml --dry-run='client' | kubectl apply -f -`

You can edit `env-kube` file and then reapply configmap with the above command. Remember to restart deployment pods with `kubectl rollout restart deployment/ufo-deployment` to apply new configmap.

### Apply manifests

```
kubectl apply -f kube/postgres/
kubectl apply -f kube/ufo/
```

### Obtain TLS certificate

Install cert-manager with `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.1/cert-manager.yaml`

Test with self-signed certificate: `kubectl apply -f kube/tls/test-selfissued.yml`
Test with staging letsencrypt certificate: `kubectl apply -f kube/tls/test-staging.yml`

Finally, obtain production letsencrypt certificate: `kubectl apply -f kube/tls/prod.yml`

### Edit environment variables

`kubectl edit configmaps ufo-config`

### Ingest database fixtures and superuser

`kubectl exec --stdin --tty deployments/ufo-deployment -- /bin/bash`

```
$ ./scripts/regions.py populatedb
$ ./scripts/2020_ankety.py
$ ./manage.py createsuperuser
```


### Port-forwarding for local testing

```
kubectl port-forward services/nginx-gateway 8080:80 --namespace nginx-gateway
```


## Deploy with Vercel / Neondb

```
zypper in postgresql
```

```
DJANGO_SETTINGS_MODULE=settings_neondb ./manage.py migrate --skip-checks
DJANGO_SETTINGS_MODULE=settings_neondb ./scripts/regions.py populatedb
```

### Deploy to Heroku
```
git remote add heroku https://git.heroku.com/spbtest-2019.git
cp env-local.example env-heroku
echo "DJANGO_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1`" >> env-heroku
export HEROKUAPP=`git remote get-url heroku | python -c "print(input().split('/')[-1][:-4])"`
```

Edit env-heroku file: set DATABASE_URL and other required variables

```
./push_heroku_env.py env-heroku
git push heroku master
heroku run sh -c './manage.py migrate --skip-checks'
heroku run sh -c './scripts/2020_ankety.py'
heroku run sh -c './scripts/regions.py populatedb'
heroku run sh -c './manage.py createsuperuser'
```

### Build and publish docker image

```
docker build --tag fak3/ufo:0.5 .
docker push fak3/ufo:0.5
```
