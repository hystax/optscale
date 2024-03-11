# How to apply SSL certificate to OptScale NGINX

Copy Key and CRT files to host as the following files: ```/tmp/key.pem``` and ```/tmp/cert.pem```

and delete old Kubernetes secret:
```
kubectl delete secret defaultcert
```
then create a new Kubernetes secret from uploaded files:
```
kubectl create secret tls defaultcert --key /tmp/key.pem --cert /tmp/cert.pem
```
and restart all NGINX Kubernetes pods: 
```
kubectl delete pod $(kubectl get pod | awk '/ngingress-nginx-ingress-controller/ {print $1}')
```
